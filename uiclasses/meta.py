# -*- coding: utf-8 -*-
from typing import List


def is_builtin_class_except(target: type, except_names: List[str]) -> bool:
    """returns ``True`` if the given class children of one of toolbelt's
    builtin metaclasses.
    """

    return target.__module__.startswith("uiclasses.") and target.__name__ in except_names


def metaclass_declaration_contains_required_attribute(
    cls: type, name: str, attrs: dict, required_attribute: str, of_type: type
):
    """validates DSL syntax of metaclass children."""
    target = f"{cls}.{required_attribute}"

    value = getattr(cls, required_attribute, None) or attrs.get(required_attribute)
    if not isinstance(value, of_type):
        raise TypeError(f"{target} must be {of_type}, got {value!r} instead.")

    return value
