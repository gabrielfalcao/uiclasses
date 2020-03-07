# -*- coding: utf-8 -*-
from typing import List


def is_builtin_class_except(target: type, except_names: List[str]) -> bool:
    """returns ``True`` if the given class children of one of metaclasses built in :py:mod:`uiclasses.base`'.
    """

    return (
        target.__module__.startswith("uiclasses.") and target.__name__ in except_names
    )
