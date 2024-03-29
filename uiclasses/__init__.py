# Copyright (c) 2020-2023 Gabriel Falcão Gonçalves de Moura

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
import warnings


if sys.version_info > (3, 6, 1):
    import typing

    if "site-packages" in typing.__file__:
        warnings.warn(
            "The typing module is installed via pip, "
            "this can cause problems in python > 3.6.2. "
            "Run `pip uninstall typing` to prevent this.",
            RuntimeWarning,
        )

from .base import (
    basic_dataclass,
    DataBag,
    DataBagChild,
    Model,
    repr_attributes,
    traverse_dict_descendants,
    try_int,
    try_json,
    UserFriendlyObject,
)
from .collections import IterableCollection, ModelList, ModelSet


__all__ = [
    "Model",
    "traverse_dict_descendants",
    "repr_attributes",
    "UserFriendlyObject",
    "DataBag",
    "DataBagChild",
    "basic_dataclass",
    "try_int",
    "try_json",
    "ModelList",
    "ModelSet",
    "IterableCollection",
]
