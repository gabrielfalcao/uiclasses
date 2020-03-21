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

import json
from typing import Any, Type, Callable, List, Union
from ordered_set import OrderedSet
from functools import reduce
from dataclasses import dataclass, fields
from uiclasses.typing import PropertyMetadata


def basic_dataclass(cls):
    """A simple alias to ``dataclasses.dataclass(init=False, eq=False, unsafe_hash=False, repr=False)``
    """
    return dataclass(init=False, eq=False, unsafe_hash=False, repr=False)(cls)


def try_convert(value: Any, convert: Callable) -> Any:
    """tries to convert the given value using the ``convert`` parameter,
    returns the value untouched in case of failure.

    Does not emit logs.
    """

    try:
        return convert(value)
    except (ValueError, json.JSONDecodeError, TypeError):
        return value


def try_dict(value):
    """tries to convert the given value to :py:class:`dict`, returns the
    value untouched in case of failure.

    Does not emit logs."""
    return try_convert(value, dict)


def try_int(value):
    """tries to convert the given value to :py:class:`int`, returns the
    value untouched in case of failure.

    Does not emit logs."""
    return try_convert(value, int)


def try_json(value: str) -> dict:
    """tries to parse the given value value as JSON, returns the value
    untouched in case of failure.

    Does not emit logs.
    """
    if not isinstance(value, str):
        return value
    return try_convert(value, json.loads)


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


def extract_attribute_from_class_definition(
    name: str, cls: Type, attrs: dict, default: Any = None
) -> Any:
    """designed for use within metaclasses to extract an attribute from
    the class definition, accepts a default as fallback"""
    return getattr(cls, name, attrs.get(name)) or default


def list_visible_field_names_from_dataclass(cls: Type):
    """lists all fields from a dataclass that does not have repr=False"""
    names = getattr(cls, "__visible_attributes__", [])
    extra = [
        f.name
        for f in fields(cls)
        if f.name not in names and f.repr and not isinstance(f.type, PropertyMetadata)
    ]
    names.extend(extra)
    return list(
        OrderedSet(names) - OrderedSet([f.name for f in extract_props_from_class(cls)])
    )


def list_field_names_from_dataclass(cls: Type):
    """lists all fields from a dataclass without filter"""
    return [f.name for f in fields(cls)]


def extract_props_from_class(cls: Type) -> List[str]:
    return filter(lambda f: isinstance(f.type, PropertyMetadata), fields(cls))


def list_getters_from_metaclass(cls: Type) -> List[str]:
    return [f.name for f in extract_props_from_class(cls) if f.type.getter]


def list_setters_from_metaclass(cls: Type) -> List[str]:
    return [f.name for f in extract_props_from_class(cls) if f.type.setter]


def get_getter_by_name(cls: Type, name: str) -> Union[PropertyMetadata, None]:
    for potential_meta in extract_props_from_class(cls):
        if not potential_meta.type.getter:
            continue
        if potential_meta.name == name:
            return potential_meta.type


def get_setter_by_name(cls: Type, name: str) -> Union[PropertyMetadata, None]:
    for potential_meta in extract_props_from_class(cls):
        if not potential_meta.type.setter:
            continue
        if potential_meta.name == name:
            return potential_meta.type
