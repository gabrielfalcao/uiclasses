import json
from typing import Any, Type, Callable
from functools import reduce
from dataclasses import dataclass, fields


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
    except (ValueError, json.JSONDecodeError):
        return value


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
    extra = [f.name for f in fields(cls) if f.name not in names and f.repr]
    names.extend(extra)
    return names


def list_field_names_from_dataclass(cls: Type):
    """lists all fields from a dataclass without filter"""
    names = getattr(cls, "__visible_attributes__", [])
    extra = [f.name for f in fields(cls) if f.name not in names]
    names.extend(extra)
    return names
