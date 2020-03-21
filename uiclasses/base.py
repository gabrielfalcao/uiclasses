# Copyright (c) 2020 NewStore GmbH

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
import json
import hashlib
import typing
import dataclasses
from typing import NewType

from dataclasses import Field
from ordered_set import OrderedSet

from typing import List, Any, Tuple
from fnmatch import fnmatch

from humanfriendly.tables import format_pretty_table
from humanfriendly.tables import format_robust_table

from . import errors
from .meta import is_builtin_class_except
from .utils import (
    basic_dataclass,
    repr_attributes,
    traverse_dict_children,
    try_int,
    try_json,
    try_dict,
    extract_attribute_from_class_definition,
    list_field_names_from_dataclass,
    list_visible_field_names_from_dataclass,
    list_getters_from_metaclass,
    list_setters_from_metaclass,
    get_getter_by_name,
    get_setter_by_name,
)
from . import typing as internal_typing
from .typing import PropertyMetadata, parse_bool

COLLECTION_TYPES = {}

if sys.version_info < (3, 7, 0):
    types_without_cast_support = (type(typing.Any), type(typing.Generic))
else:
    types_without_cast_support = (typing._SpecialForm, typing._GenericAlias)


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
        return parse_bool(value)


class DataBagChild(DataBag):
    """Represents a nested dict within a DataBag that is aware of its
    location within the parent.
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


class MetaModel(type):
    """metaclass for data models
    """

    def __init__(cls, name, bases, attrs):
        if is_builtin_model(cls):
            return

        basic_dataclass(cls)  # required by dataclasses.fields(cls)

        known_getters = list_getters_from_metaclass(cls)
        attrs["__known_getters__"] = known_getters
        cls.__known_getters__ = known_getters

        known_setters = list_setters_from_metaclass(cls)
        attrs["__known_setters__"] = known_setters
        cls.__known_setters__ = known_setters

        visible = []

        from_annotations = list_visible_field_names_from_dataclass(cls)
        from_dunder_declaration = filter(
            lambda name: name not in from_annotations,
            extract_attribute_from_class_definition(
                "__visible_attributes__", cls, attrs, default=visible
            ),
        )
        visible.extend(from_annotations)
        visible.extend(from_dunder_declaration)

        visible = list(OrderedSet(visible) - OrderedSet(known_setters))
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

        SetName = f"{name}.Set"
        cls.Set = attrs["Set"] = type(
            SetName, (COLLECTION_TYPES[set],), {"__of_model__": cls}
        )
        cls.Set.Type = internal_typing.ModelSet[cls]
        ListName = f"{name}.List"
        cls.List = attrs["List"] = type(
            ListName, (COLLECTION_TYPES[list],), {"__of_model__": cls}
        )
        cls.List.Type = internal_typing.ModelList[cls]


class Model(DataBag, metaclass=MetaModel):
    """Base class for User-interface classes.

    Allows declaring what instance attributes are visible via type
    annotations or ``__visible_attributes__``.

    Example:


    .. code::

       from uiclasses.base import Model

       class BlogPost(Model):
           id: int
           title: str


        post = BlogPost(
            id=1,
            title='test',
            body='lorem ipsum dolor sit amet'
        )

        print(str(post))
        print(repr(post))
        print(post.format_robust_table())

    """

    __visible_attributes__: List[str]

    def __init__(self, __data__: dict = None, *args, **kw):
        __data__ = __data__ or {}
        if isinstance(__data__, Model):
            __data__ = __data__.serialize()

        __data__ = try_dict(__data__)
        if not isinstance(__data__, dict):
            raise TypeError(
                f"{self.__class__.__name__} received a non-dict "
                f"__data__ argument: {__data__!r}"
            )

        known_fields = dict([(f.name, f) for f in dataclasses.fields(self.__class__)])
        for name in list(__data__.keys()):
            value = __data__.get(name)
            if value is None:
                continue

            field = known_fields.get(name)
            if field and field.type:
                cast_field(field, value)

        for name in list(kw.keys()):
            value = kw.get(name)

            field = known_fields.get(name)
            if field and field.type:
                cast_field(field, value)

            __data__[name] = value

        self.__data__ = __data__
        self.initialize(*args, **kw)

    def __getattr__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            meta_getter = get_getter_by_name(self.__class__, attr)

            if attr not in allowed_getters(self.__class__):
                raise

            meta_getter = get_getter_by_name(self.__class__, attr)
            value = self.__data__.get(attr)
            if meta_getter:
                value = meta_getter.cast(value)

            return value

    def __setattr__(self, attr, value):
        if attr in allowed_setters(self.__class__):
            meta_setter = get_setter_by_name(self.__class__, attr)
            if meta_setter:
                value = meta_setter.cast(value)

            self.__data__[attr] = value
        elif attr.startswith("__") or hasattr(self, attr):
            super().__setattr__(attr, value)
        else:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {attr!r}"
            )

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
                for name in list_visible_field_names_from_dataclass(self.__class__)
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


def allowed_getters(cls: Model):
    return set(cls.__known_getters__).union(set(cls.__visible_attributes__))


def allowed_setters(cls: Model):
    return set(cls.__known_setters__).union(set(cls.__visible_attributes__))


def cast_field(field, value):
    name = field.name
    if field.type == bool:
        value = parse_bool(value)

    if isinstance(field.type, types_without_cast_support):
        pass  # can't cast from typing.Any or typing.Generic

    elif isinstance(field.type, PropertyMetadata):
        value = field.type.cast(value)

    elif not isinstance(value, field.type):
        raise TypeError(f"{name} is not a {field.type}: {value!r}")

    return value
