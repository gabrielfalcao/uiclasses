import json
import hashlib
import dataclasses

from dataclasses import Field

from typing import List, Any, Tuple, Type
from fnmatch import fnmatch
from functools import reduce

from humanfriendly.tables import format_robust_table, format_pretty_table

from . import errors
from .meta import is_builtin_class_except


COLLECTION_TYPES = {}


basic_dataclass = dataclasses.dataclass(
    init=False, eq=False, unsafe_hash=False, repr=False
)


def try_convert(value, convert):
    try:
        return convert(value)
    except (ValueError, json.JSONDecodeError):
        return value


def try_int(s):
    return try_convert(s, int)


def try_json(string: str) -> dict:
    return try_convert(string, json.loads)


def traverse_dict_children(data, *keys, fallback=None):
    """attempts to retrieve the config value under the given nested keys
    """
    value = reduce(lambda d, l: d.get(l, None) or {}, keys, data)
    return value or fallback


def repr_attributes(attributes: dict, separator: str = " "):
    """used for pretty-printing the attributes of a model
    :param attributes: a dict

    :returns: a string
    """
    return separator.join([f"{k}={v!r}" for k, v in attributes.items()])


@basic_dataclass
class UserFriendlyObject(object):
    def __ui_name__(self):
        return self.__class__.__name__

    def __get_field_value__(self, field: Field) -> Any:
        default_value = field.type()
        return getattr(self, field.name, default_value)

    def __get_field_keyvalue__(self, field: Field) -> Tuple[str, Any]:
        return (field.name, self.__get_field_value__(field))

    def __ui_attributes__(self):
        fields = dataclasses.fields(self)
        return dict(map(self.__get_field_keyvalue__, fields))

    def __repr__(self):
        attributes = repr_attributes(self.__ui_attributes__())
        return f"<{self.__ui_name__()} {attributes}>"

    def __str__(self):
        attributes = repr_attributes(self.__ui_attributes__(), ", ")
        return f"{self.__ui_name__()}({attributes})"


class DataBag(UserFriendlyObject):
    """base-class for config containers, behaves like a dictionary but is
    a enhanced proxy to manage data from its internal dict
    ``__data__`` as well as traversing nested dictionaries within
    it."""

    def __init__(self, __data__: dict = None):
        __data__ = __data__ or {}
        if not isinstance(__data__, dict):
            raise TypeError(
                f"{self.__class__.__name__}() requires a dict object, "
                f"but instead got '{__data__} {type(__data__)}'."
            )

        self.__data__ = __data__

    def __bool__(self):
        return bool(self.__data__)

    def update(self, other: dict):
        self.__data__.update(other or {})

    def traverse(self, *keys, fallback=None):
        """attempts to retrieve the config value under the given nested keys
        """
        value = traverse_dict_children(self.__data__, *keys, fallback=fallback)
        if isinstance(value, dict):
            return DataBagChild(value, *keys)

        return value

    def __ui_attributes__(self):
        """converts self.__data__ to dict to prevent recursion error
        """
        return dict(self.__data__)

    # rudimentary dict compatibility:

    def __iter__(self):
        return iter(self.__data__)

    def __getitem__(self, item):
        return self.__data__[item]

    def __setitem__(self, item, value):
        self.__data__[item] = value

    def keys(self):
        return self.__data__.keys()

    def items(self):
        return self.__data__.items()

    def values(self):
        return self.__data__.values()

    def get(self, *args, **kw):
        return self.__data__.get(*args, **kw)

    # other handy methods:

    def getbool(self, *args, **kw):
        """same as .get() but parses the string value into boolean: `yes` or
        `true`"""
        value = self.get(*args, **kw)
        if not isinstance(value, str):
            return bool(value)

        value = value.lower().strip()
        return value in ("yes", "true", "1", "t")


class DataBagChild(DataBag):
    """
    """

    def __init__(self, data, *location):
        self.location = location
        self.attr = ".".join(location)
        super().__init__(data)

    def __ui_attributes__(self):
        """converts self.__data__ to dict to prevent recursion error
        """
        return dict(self.__data__)

    def __ui_name__(self):
        return f"DataBagChild {self.attr!r} of "


def is_builtin_model(target: type) -> bool:
    """returns ``True`` if the given type is a model subclass"""

    return is_builtin_class_except(target, ["MetaModel", "Model", "DataBag"])


def extract_attribute_from_class_definition(
    name: str, cls: Type, attrs: dict, default: Any = None
) -> Any:
    return getattr(cls, name, attrs.get(name)) or default


def list_visible_field_names_from_dataclass(cls: Type):
    return [f.name for f in dataclasses.fields(cls) if f.repr]


def list_field_names_from_dataclass(cls: Type):
    return [f.name for f in dataclasses.fields(cls)]


class MetaModel(type):
    """metaclass for data models
    """

    def __init__(cls, name, bases, attrs):
        if is_builtin_model(cls):
            return

        basic_dataclass(cls)  # required by dataclasses.fields(cls)

        visible = extract_attribute_from_class_definition(
            "__visible_attributes__", cls, attrs, default=[]
        )
        visible.extend(
            filter(
                lambda name: name not in visible,
                list_visible_field_names_from_dataclass(cls),
            )
        )
        attrs["__visible_attributes__"] = visible
        cls.__visible_attributes__ = visible

        ids = extract_attribute_from_class_definition(
            "__id_attributes__", cls, attrs, default=[]
        )

        ids.extend(
            filter(lambda name: name not in ids, list_field_names_from_dataclass(cls))
        )
        attrs["__id_attributes__"] = ids
        cls.__id_attributes__ = ids

        cls.Set = attrs["Set"] = type(
            f"{name}.Set", (COLLECTION_TYPES[set],), {"__of_model__": cls}
        )
        cls.List = attrs["List"] = type(
            f"{name}.List", (COLLECTION_TYPES[list],), {"__of_model__": cls}
        )

        super().__init__(name, bases, attrs)


class Model(DataBag, metaclass=MetaModel):
    """Base model for data in all domains, from boto3 responses to
    command-line output of kubernetes tools such as kubectl, kubectx.
    """

    __visible_attributes__: List[str]

    def __init__(self, __data__: dict = None, *args, **kw):
        __data__ = __data__ or {}
        if isinstance(__data__, Model):
            __data__ = __data__.serialize()

        if not isinstance(__data__, dict):
            raise TypeError(
                f"{self.__class__.__name__} received a non-dict __data__ argument: {__data__!r}"
            )

        for field in dataclasses.fields(self.__class__):
            if field.name not in kw:
                continue

            # value = try_convert(kw.pop(field.name), field.type)
            value = kw.pop(field.name)
            if field.type and not isinstance(value, field.type):
                raise TypeError(f"{field.name} is not a {field.type}: {value!r}")

            __data__[field.name] = value

        self.__data__ = __data__
        self.initialize(*args, **kw)

    def initialize(self, *args, **kw):
        """this method is a no-op, use it to take action after the model has
        been completely instantiated without having to override __init__ and call super().
        """

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return other.__ui_attributes__() == self.__ui_attributes__()

    def __hash__(self):
        values = dict([(k, try_int(self.get(k))) for k in self.__id_attributes__])
        string = json.dumps(values)
        return int(hashlib.sha1(bytes(string, "ascii")).hexdigest(), 16)

    def serialize(self) -> dict:
        data = self.__data__.copy()
        for field in dataclasses.fields(self.__class__):
            if field.type == bool:
                data[field.name] = self.getbool(field.name)

        return data

    def to_dict(self):
        return self.serialize()

    @classmethod
    def from_json(cls, json_string: str) -> "Model":
        data = try_json(json_string)
        if not isinstance(data, dict):
            raise errors.InvalidJSON(f"{json_string!r} cannot be parsed as a dict")

        return cls(data)

    def to_json(self, *args, **kw):
        kw["default"] = kw.pop("default", str)
        return json.dumps(self.to_dict(), *args, **kw)

    def __ui_attributes__(self):
        return dict(
            [
                (name, getattr(self, name, self.get(name)))
                for name in self.__visible_attributes__
            ]
        )

    def attribute_matches(self, attribute_name: str, fnmatch_pattern: str) -> bool:

        """helper method to filter models by an attribute. This allows for
        :py:class:`~uiclasses.ModelList` to
        :py:meth:`~uiclasses.ModelList.filter_by`.
        """
        value = getattr(self, attribute_name, self.get(attribute_name))
        if isinstance(fnmatch_pattern, str):
            return fnmatch(value or "", fnmatch_pattern or "")
        else:
            return value == fnmatch_pattern

    def get_table_columns(self):
        return self.__class__.__visible_attributes__

    def get_table_rows(self):
        return [list(self.__ui_attributes__().values())]

    def get_table_columns_and_rows(self):
        columns = self.get_table_columns()
        rows = self.get_table_rows()
        return columns, rows

    def format_robust_table(self):
        columns, rows = self.get_table_columns_and_rows()
        return format_robust_table(rows, columns)

    def format_pretty_table(self):
        columns, rows = self.get_table_columns_and_rows()
        return format_pretty_table(rows, columns)
