import re
import json
import hashlib
import logging
import dataclasses

from typing import List
from fnmatch import fnmatch
from functools import reduce

from humanfriendly.tables import format_robust_table, format_pretty_table
from .meta import (
    is_builtin_class_except,
)


logger = logging.getLogger(__name__)
COLLECTION_TYPES = {}


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


class UserFriendlyObject(object):
    def __ui_name__(self):
        return self.__class__.__name__

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

    @property
    def data(self):
        return self.__data__

    def update(self, other: dict):
        self.data.update(other or {})

    def traverse(self, *keys, fallback=None):
        """attempts to retrieve the config value under the given nested keys
        """
        value = traverse_dict_children(self.data, *keys, fallback=fallback)
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
        return self.data.items()

    def values(self):
        return self.data.values()

    def get(self, *args, **kw):
        return self.data.get(*args, **kw)

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


def try_int(s):
    try:
        return int(s)
    except ValueError:
        return s


def try_json(string: str) -> dict:
    return json.loads(string)


def slugify(text: str, separator: str = "-"):
    return re.sub(
        fr"[{separator}]+", separator,
        re.sub(r"[^a-zA-Z0-9-]+", separator, text).strip(separator))


def is_builtin_model(target: type) -> bool:
    """returns ``True`` if the given type is a model subclass"""

    return is_builtin_class_except(target, ["MetaModel", "Model", "DataBag"])


class MetaModel(type):
    """metaclass for data models
    """

    def __init__(cls, name, bases, attrs):
        if is_builtin_model(cls):
            return

        dataclasses.dataclass(init=False, eq=False, unsafe_hash=False, repr=False)(cls)
        __visible_atttributes__ = getattr(cls, '__visible_atttributes__', attrs.get('__visible_atttributes__')) or []
        __visible_atttributes__.extend([f.name for f in dataclasses.fields(cls) if f.repr and f.name not in __visible_atttributes__])
        attrs['__visible_atttributes__'] = __visible_atttributes__
        cls.__visible_atttributes__ = __visible_atttributes__

        __id_attributes__ = getattr(cls, '__id_attributes__', attrs.get('__id_attributes__')) or []
        __id_attributes__.extend([f.name for f in dataclasses.fields(cls) if f.repr and f.name not in __id_attributes__])
        attrs['__id_attributes__'] = __id_attributes__
        cls.__id_attributes__ = __id_attributes__
        super().__init__(name, bases, attrs)


class Model(DataBag, metaclass=MetaModel):
    """Base model for data in all domains, from boto3 responses to
    command-line output of kubernetes tools such as kubectl, kubectx.
    """

    __visible_atttributes__: List[str]

    def __init__(self, __data__: dict = None, *args, **kw):
        __data__ = __data__ or {}
        if isinstance(__data__, Model):
            __data__ = __data__.serialize()

        if not isinstance(__data__, dict):
            raise TypeError(
                f'{self.__class__.__name__} received a non-dict __data__ argument: {__data__!r}'
            )

        for field in dataclasses.fields(self.__class__):
            if field.name not in kw:
                continue
            value = kw.pop(field.name)
            if field.type and not isinstance(value, field.type):
                raise TypeError(
                    f'{field.name} is not a {field.type}: {value!r}'
                )

            __data__[field.name] = value

        self.__data__ = __data__
        self.initialize(*args, **kw)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return other.__ui_attributes__() == self.__ui_attributes__()

    def __id__(self):
        return sum(
            filter(
                lambda v: isinstance(v, int),
                [try_int(self.get(k)) for k in self.__id_attributes__],
            )
        )

    def __hash__(self):
        values = dict(
            [(k, try_int(self.get(k))) for k in self.__id_attributes__]
        )
        string = json.dumps(values)
        return int(hashlib.sha1(bytes(string, "ascii")).hexdigest(), 16)

    def __nonzero__(self):
        return any(list(self.__data__.values()))

    def initialize(self, *args, **kw):
        pass

    def update(self, data: dict):
        self.__data__.update(data)

    def serialize(self) -> dict:
        data = self.__data__.copy()
        for field in dataclasses.fields(self.__class__):
            if field.type == bool:
                data[field.name] = self.getbool(field.name)

        return data

    def to_dict(self):
        return self.serialize()

    @classmethod
    def from_json(cls, json_string: str) -> "uiclasses.Model":
        data = try_json(json_string)
        return cls(data)

    def to_json(self, *args, **kw):
        kw["default"] = kw.pop("default", str)
        return json.dumps(self.to_dict(), *args, **kw)

    def __getitem__(self, key):
        return self.__data__.get(key, None)

    def get(self, *args, **kw):
        return self.__data__.get(*args, **kw)

    def __ui_attributes__(self):
        return dict(
            [
                (name, getattr(self, name, self.get(name)))
                for name in self.__visible_atttributes__
            ]
        )

    def attribute_matches_glob(self, attribute_name: str, fnmatch_pattern: str) -> bool:
        """helper method to filter models by an attribute. This allows for
        :py:class:`~uiclasses.ModelList` to
        :py:meth:`~uiclasses.ModelList.filter_by`.
        """
        try:
            value = getattr(self, attribute_name, self.get(attribute_name))
        except AttributeError as e:
            raise RuntimeError(
                f"{self} does not have a {attribute_name!r} attribute: {e}"
            )

        if isinstance(fnmatch_pattern, str):
            return fnmatch(value or "", fnmatch_pattern or "")
        else:
            return value == fnmatch_pattern

    @classmethod
    def List(cls, *items):
        ModelList = COLLECTION_TYPES[list]
        return ModelList(cls, list(items))

    @classmethod
    def Set(cls, *items):
        ModelSet = COLLECTION_TYPES[set]
        return ModelSet(cls, items)

    def get_table_columns(self):
        return self.__class__.__visible_atttributes__

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