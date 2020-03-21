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
import typing
from typing import Union, Any, Type, List, Set


def parse_bool(value):
    if not isinstance(value, str):
        return bool(value)

    value = value.lower().strip()
    return value in ("yes", "true", "1", "t")


class MetaModelList(type):
    def __getitem__(cls, key):
        return getattr(key, "List", List)


class MetaModelSet(type):
    def __getitem__(cls, key):
        return getattr(key, "Set", Set)


class MetaIterableCollection(type):
    def __getitem__(cls, key):
        return Union[ModelList[key], ModelSet[key]]


class PropertyMetadata(object):
    def __init__(self, Type: Type, getter=False, setter=False):
        self.Type = Type
        self.getter = getter
        self.setter = setter

    def cast(self, value):
        if self.Type == bool:
            return parse_bool(value)

        return typing.cast(self.Type, value)


class MetaGetter(type):
    def __getitem__(cls, key: Any):
        return PropertyMetadata(key, getter=True)


class MetaSetter(type):
    def __getitem__(cls, key: Any):
        return PropertyMetadata(key, setter=True)


class MetaProperty(type):
    def __getitem__(cls, key: Any):
        return PropertyMetadata(key, setter=True, getter=True)


class Getter(metaclass=MetaGetter):
    pass


class Setter(metaclass=MetaSetter):
    pass


class Property(metaclass=MetaProperty):
    pass


class ModelList(metaclass=MetaModelList):
    pass


class ModelSet(metaclass=MetaModelSet):
    pass


class IterableCollection(metaclass=MetaIterableCollection):
    pass
