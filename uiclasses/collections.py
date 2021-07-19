# Copyright (c) 2020 Gabriel Falcao

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

import itertools

from collections.abc import Sized
from types import GeneratorType
from typing import Callable
from typing import Iterable as IterableType
from typing import TypeVar

from humanfriendly.tables import format_pretty_table, format_robust_table
from ordered_set import OrderedSet

from . import typing as internal_typing
from .base import COLLECTION_TYPES, Model, UserFriendlyObject


ITERABLES = (list, tuple, itertools.chain, set, map, filter, GeneratorType)
T = TypeVar("T")


def is_iterable(values) -> bool:
    return any(
        [
            isinstance(values, ITERABLES + (IterableCollection,)),
            callable(getattr(values, "__iter__", None)),
        ]
    )


class IterableCollection(UserFriendlyObject, Sized, IterableType[T]):
    """Base mixin for ModelList and ModelSet, provides methods to
    manipulate iterable collections in ways take advantage of the
    behavior of models.


    For example it supports filtering by instance attributes through a cal to the
    :py:meth:`~uiclasses.base.Model.attribute_matches` method of each children.

    **Features:**

    - :py:meth:`~uiclasses.collections.IterableCollection.sorted_by` - sort by a single attribute
    - :py:meth:`~uiclasses.collections.IterableCollection.filter_by` - to filter by a single attribute
    - :py:meth:`~uiclasses.collections.IterableCollection.sorted` - alias to ``MyModel.List(sorted(my_model_collection))`` or ``.Set()``
    - :py:meth:`~uiclasses.collections.IterableCollection.filter` - alias to ``MyModel.List(filter(callback, my_model_collection))``
    - :py:meth:`~uiclasses.collections.IterableCollection.format_robust_table`
    - :py:meth:`~uiclasses.collections.IterableCollection.format_pretty_table`
    """

    __visible_attributes__ = ["model_class"]

    def __repr__(self):
        return f"<{self.__ui_name__()} {list(self)}>"

    def __str__(self):
        return f"{self.__ui_name__()}[length={len(self)}]"

    def __iter__(self) -> IterableType[T]:
        for x in super().__iter__():
            yield x

    def __len__(self) -> int:
        return super().__len__()

    def sorted(self, **kw):
        """returns a new ``ModelList`` with this collections' children sorted.

        Example:

        .. code::

           x = MyModel.List([MyModel({"id": 2}), MyModel({"id": 3})])
           result = x.sorted(key=lambda model: model.id)

        """

        items = sorted(self, **kw)
        return self.__class__(items)

    def sorted_by(self, attribute: str, **kw):
        """sort by a single attribute of the model children.

        Example:

        .. code::

           x = MyModel.List([MyModel({"id": 2}), MyModel({"id": 3})])
           result = x.sorted_by('id')

        """
        return self.sorted(
            key=lambda model: getattr(model, attribute, model.get(attribute))
            or "",
            **kw,
        )

    def filter_by(
        self, attribute_name: str, fnmatch_pattern: str
    ) -> internal_typing.IterableCollection[Model]:
        """filter by a single attribute of the model children.

        Example:

        .. code::

           x = MyModel.List([MyModel({"name": 'chucknorris'}), MyModel({"name": 'foobar'})])
           result = x.filter_by('name', '*norris*')

        """
        return self.filter(
            lambda model: model.attribute_matches(
                attribute_name, fnmatch_pattern
            )
        )

    def filter(self, check: Callable[[Model], bool]) -> IterableType[Model]:
        """returns a new ``ModelList`` with this collections' children filter.

        Example:

        .. code::

           x = MyModel.List([MyModel({"id": 2}), MyModel({"id": 3})])
           result = x.filter(key=lambda model: model.id)
        """
        results = filter(check, self)
        return self.__class__(results)

    def get_table_columns(self, columns: IterableType[str] = None):
        """proxy to :py:meth:`~uiclasses.base.Model.get_table_columns`"""
        available_columns = self.__of_model__.__visible_attributes__
        if not isinstance(columns, list):
            return available_columns

        return self.validate_columns(columns)

    def get_table_rows(self, columns: IterableType[str] = None):
        """returns a list of values from the __ui_attributes__ of each child of this collection.

        Used by
        :py:meth:`~uiclasses.collections.IterableCollection.format_robust_table`
        and
        :py:meth:`~uiclasses.collections.IterableCollection.format_pretty_table`.

        """
        columns = self.get_table_columns(columns)
        return [
            [model.__ui_attributes__().get(key) for key in columns]
            for model in self
        ]

    def get_table_columns_and_rows(self, columns: IterableType[str] = None):
        """returns a 2-item tuple with columns names and row values of each
        child of this collection.

        Used by
        :py:meth:`~uiclasses.collections.IterableCollection.format_robust_table`
        and
        :py:meth:`~uiclasses.collections.IterableCollection.format_pretty_table`.

        """
        columns = self.get_table_columns(columns)
        rows = self.get_table_rows(columns)
        return columns, rows

    def format_robust_table(self, columns: IterableType[str] = None):
        """returns a string with a robust table ready to be printed on a terminal.

        powered by :py:func:`humanfriendly.tables.format_robust_table`
        """
        columns, rows = self.get_table_columns_and_rows(columns)
        return format_robust_table(rows, columns)

    def format_pretty_table(self, columns: IterableType[str] = None):
        """returns a string with a pretty table ready to be printed on a terminal.

        powered by :py:func:`humanfriendly.tables.format_pretty_table`
        """
        columns, rows = self.get_table_columns_and_rows(columns)
        return format_pretty_table(rows, columns)

    def validate_columns(self, columns):

        mismatched_columns = set(columns).difference(
            self.__of_model__.__visible_attributes__
        )
        if mismatched_columns:
            raise ValueError(
                f"the following columns are not available "
                f"for {self.__of_model__}: {mismatched_columns}"
            )

        return columns

    def to_dict(self, only_visible: bool = False) -> IterableType[dict]:
        """calls ``.to_dict()`` in each children of this collection."""
        return [m.to_dict(only_visible=only_visible) for m in self]

    def serialize(self, only_visible: bool = False) -> IterableType[dict]:
        """calls ``.serialize()`` in each children of this collection."""
        return [m.serialize(only_visible=only_visible) for m in self]

    def serialize_visible(self) -> IterableType[dict]:
        """calls ``.serialize_visible()`` in each children of this collection."""
        return [m.serialize_visible() for m in self]

    def serialize_all(self) -> IterableType[dict]:
        """calls ``.serialize_all()`` in each children of this collection."""
        return [m.serialize_all() for m in self]


class ModelList(list, IterableCollection[T]):
    """Implementation of :py:class:`~uiclasses.collections.IterableCollection` for the
    :py:class:`list` type.

    """

    def __init__(self, children: IterableType[T]):
        model_class = self.__of_model__

        if not is_iterable(children):
            raise TypeError(
                f"{self.__class__.__name__} requires the 'children' attribute to be "
                f"a valid iterable, got {children!r} {type(children)} instead"
            )

        items = []
        for index, child in enumerate(children):
            if isinstance(child, dict):
                child = self.__of_model__(child)
            if not isinstance(child, model_class):
                raise TypeError(
                    f"cannot create {self.__class__.__name__} because value at index [{index}] is not a {model_class}: {child!r} {type(child)}"
                )
            items.append(child)

        super().__init__(map(model_class, items))

    def unique(self) -> "ModelSet":
        """returns a :py:class:`~uiclasses.collections.ModelSet` of all unique items in this :py:class:`~uiclasses.collections.ModelList`"""
        return self.__of_model__.Set(self)

    def __iter__(self) -> IterableType[T]:
        for x in super().__iter__():
            yield x

    def __len__(self) -> int:
        return super().__len__()


class ModelSet(OrderedSet, IterableCollection):
    """Implementation of :py:class:`~uiclasses.collections.IterableCollection` for the
    `OrderedSet <https://pypi.org/project/ordered-set/>`_ type.
    """

    def __init__(self, children: IterableType[Model]):
        model_class = getattr(self, "__of_model__", None)

        if not is_iterable(children):
            raise TypeError(
                f"{self.__class__.__name__} requires the 'children' attribute to be "
                f"a valid iterable, got {children!r} {type(children)} instead"
            )
        items = []
        for index, child in enumerate(children):
            if isinstance(child, dict):
                child = self.__of_model__(child)

            if not isinstance(child, model_class):
                raise TypeError(
                    f"cannot create {self.__class__.__name__} because value at index [{index}] is not a {model_class}: {child!r} {type(child)}"
                )
            items.append(child)

        super().__init__(map(model_class, items))


COLLECTION_TYPES[iter] = IterableCollection
COLLECTION_TYPES[list] = ModelList
COLLECTION_TYPES[set] = ModelSet
COLLECTION_TYPES[OrderedSet] = ModelSet
