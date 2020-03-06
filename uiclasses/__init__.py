"""
contains generic implementations used across the codebase. Mainly data-models
"""
import re
import json
import pendulum
import itertools
import logging

from datetime import datetime
from typing import List, Callable
from fnmatch import fnmatch
from functools import reduce
from ordered_set import OrderedSet

from humanfriendly.tables import format_robust_table, format_pretty_table
from .meta import (
    is_builtin_class_except,
    metaclass_declaration_contains_required_attribute,
)

from .fs import store_models, load_models


ITERABLES = (list, tuple, itertools.chain, set, map)

logger = logging.getLogger(__name__)


def traverse_dict_children(data, *keys, fallback=None):
    """attempts to retrieve the config value under the given nested keys
    """
    value = reduce(lambda d, l: d.get(l, None) or {}, keys, data)
    return value or fallback


def pretty_json(data, indent=2):
    """serializes the given data into JSON with indentation"""
    return json.dumps(data, indent=2, default=str)


def repr_attributes(attributes: dict, separator: str = " "):
    """used for pretty-printing the attributes of a model
    :param attributes: a dict

    :returns: a string
    """
    return separator.join([f"{k}={v!r}" for k, v in attributes.items()])


def object_is_user_friendly(obj: object) -> bool:
    """check if the given object is user-friendly to be printed on the UI"""
    if isinstance(obj, UserFriendlyObject):
        return True

    if isinstance(obj, (list, tuple, set, bool, str, bytes, int)):
        return True

    return False


class UserFriendlyObject(object):
    def __ui_attributes__(self):
        return dict(
            [
                (key, value)
                for key, value in self.__dict__.items()
                if object_is_user_friendly(value)
            ]
        )

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

    def __init__(self, data: dict = None, *args, **kw):
        data = data or {}
        if not isinstance(data, dict):
            raise TypeError(
                f"{self.__class__.__name__}() requires a dict object, "
                f"but instead got '{data} {type(data)}'."
            )

        self.__data__ = data

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
        return value in ("yes", "true")


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


def try_json(string: str) -> dict:
    try:
        return json.loads(string)
    except Exception:
        logger.exception(f"failed to parse json string {string!r}")


def slugify(text: str, separator: str = "-"):
    return re.sub(
        fr"[{separator}]+", separator,
        re.sub(r"[^a-zA-Z0-9-]+", separator, text).strip(separator))


def ensure_datetime(value):
    if isinstance(value, str):
        return pendulum.parse(value)
    if isinstance(value, datetime):
        return pendulum.instance(value)
    if isinstance(value, pendulum.DateTime):
        return value

    return value


def is_builtin_model(target: type) -> bool:
    """returns ``True`` if the given type is a model subclass"""

    return is_builtin_class_except(target, ["MetaModel", "Model", "DataBag"])


def validate_model_declaration(cls, name, attrs):
    """validates model class definitions"""
    target = f"{cls}.__visible_atttributes__"

    if not is_builtin_model(cls):
        return

    visible_atttributes = metaclass_declaration_contains_required_attribute(
        cls, name, attrs, "visible_atttributes", str
    )

    if not isinstance(visible_atttributes, (tuple, list)):
        raise TypeError(f"{target} must be a list of strings")

    for index, field in enumerate(visible_atttributes):
        if isinstance(field, str):
            continue

        raise TypeError(
            f"{target}[{index}] should be a string, "
            f"but is {field!r} ({type(field)})"
        )


class MetaModel(type):
    """metaclass for data models
    """

    def __init__(cls, name, bases, attrs):
        if is_builtin_model(cls):
            return

        if not is_builtin_model(cls):
            validate_model_declaration(cls, name, attrs)

        super().__init__(name, bases, attrs)


class Model(DataBag, metaclass=MetaModel):
    """Base model for data in all domains, from boto3 responses to
    command-line output of kubernetes tools such as kubectl, kubectx.
    """

    __visible_atttributes__: List[str] = []

    def __init__(self, data: dict = None, *args, **kw):
        if isinstance(data, UserFriendlyObject):
            data = data.serialize()

        self.__data__ = data or {}
        self.initialize(*args, **kw)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return other.__ui_attributes__() == self.__ui_attributes__()

    def __nonzero__(self):
        return any(list(self.__data__.values()))

    def initialize(self, *args, **kw):
        pass

    def update(self, data: dict):
        self.__data__.update(data)

    def serialize(self):
        return self.__data__.copy()

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
        return ModelList(cls, *items)

    def get_table_columns(self):
        return self.__class__.__visible_atttributes__

    def get_table_rows(self):
        return [list(self.__ui_attributes__().values())]

    def get_table_colums_and_rows(self):
        columns = self.get_table_columns()
        rows = self.get_table_rows()
        return columns, rows

    def format_robust_table(self):
        columns, rows = self.get_table_colums_and_rows()
        return format_robust_table(rows, columns)

    def format_pretty_table(self):
        columns, rows = self.get_table_colums_and_rows()
        return format_pretty_table(rows, columns)


class IterableCollection(UserFriendlyObject):
    """Base mixin for ModelList and ModelSet, provides methods to
    manipulate iterable collections in ways take advantage of the
    behavior of models.


    For example it supports filtering by instance attributes through a cal to the
    :py:meth:`~uiclasses.Model.attribute_matches_glob` method of each children.

    Features:

    - sort by ``model.__ui_attributes__`` :py:meth:`~uiclasses.IterableCollection.sorted`
    - filter with a lambda :meth:`~uiclasses.IterableCollection.filter`
    - map to a lambda :meth:`~uiclasses.IterableCollection.map`
    - filter by ``model.__ui_attributes__`` :meth:`~uiclasses.IterableCollection.filter_by`
    - format robust table for console based on __ui_attributes__ :meth:`~uiclasses.IterableCollection.format_robust_table`
    - format pretty table for console based on __ui_attributes__ :meth:`~uiclasses.IterableCollection.format_pretty_table`

    """
    __visible_atttributes__ = ['count']

    @property
    def count(self):
        return len(self)

    def initialize(self, model_class: type):
        if not isinstance(model_class, type) or not issubclass(model_class, Model):
            raise TypeError(
                f"ModelList requires the 'model_class' attribute to be "
                "a Model subclass, got {model_class!r} instead"
            )

        self.model_class = model_class

    def sorted(self, **kw):
        """returns a new ``ModelList`` with this collections' children sorted.

        Example:

        .. code::

           x = ModelList([MyModel({"id": 2}), MyModel({"id": 3})])
           result = x.sorted(key=lambda model: model.id)

        """

        try:
            items = sorted(self, **kw)
        except TypeError as error:
            raise TypeError(
                f"when sorting a list of {self.model_class} objects with {kw}: {error}"
            )
        return self.model_class.List(items)

    def sorted_by(self, attribute: str, **kw):
        """sort by a single attribute of the model children.

        Example:

        .. code::

           x = ModelList([MyModel({"id": 2}), MyModel({"id": 3})])
           result = x.sort_by('id')

        """
        return self.sorted(
            key=lambda model: getattr(model, attribute, model.get(attribute)) or "",
            **kw,
        )

    def filter_by(self, attribute_name: str, fnmatch_pattern: str) -> List[Model]:
        """filter by a single attribute of the model children.

        Example:

        .. code::

           x = ModelList([MyModel({"name": 'chucknorris'}), MyModel({"name": 'foobar'})])
           result = x.filter_by('name', '*norris*')

        """
        return self.filter(
            lambda model: model.attribute_matches_glob(attribute_name, fnmatch_pattern)
        )

    def filter(self, check: Callable[[Model], bool]) -> List[Model]:
        """returns a new ``ModelList`` with this collections' children filter.

        Example:

        .. code::

           x = ModelList([MyModel({"id": 2}), MyModel({"id": 3})])
           result = x.filter(key=lambda model: model.id)
        """
        results = []
        for index, model in enumerate(self):
            if not isinstance(model, self.model_class):
                raise ValueError(
                    f"{self}[{index}] is not an instance of {self.model_class}"
                )
            if check(model):
                results.append(model)

        return self.model_class.List(results)

    def get_table_columns(self, columns: List[str] = None):
        """proxy to :py:meth:`uiclasses.Model.get_table_columns`
        """
        available_columns = self.model_class.__visible_atttributes__
        if not isinstance(columns, list):
            return available_columns

        return self.validate_columns(columns)

    def get_table_rows(self, columns: List[str] = None):
        """returns a list of values from the __ui_attributes__ of each child of this collection.

        Used by
        :py:meth:`uiclasses.IterableCollection.format_robust_table`
        and
        :py:meth:`uiclasses.IterableCollection.format_pretty_table`.

        """
        if columns:
            columns = self.get_table_columns(columns)

        if isinstance(columns, list):
            return [[model.__ui_attributes__().get(key) for key in columns] for model in self]

        return [list(model.__ui_attributes__().values()) for model in self]

    def get_table_colums_and_rows(self, columns: List[str] = None):
        """returns a 2-item tuple with columns names and row values of each
        child of this collection.

        Used by
        :py:meth:`uiclasses.IterableCollection.format_robust_table`
        and
        :py:meth:`uiclasses.IterableCollection.format_pretty_table`.

        """
        columns = self.get_table_columns(columns)
        rows = self.get_table_rows(columns)
        return columns, rows

    def format_robust_table(self, columns: List[str] = None):
        """returns a string with a robust table ready to be printed on a terminal.

        powered by :py:func:`humanfriendly.tables.format_robust_table`
        """
        columns, rows = self.get_table_colums_and_rows(columns)
        return format_robust_table(rows, columns)

    def format_pretty_table(self, columns: List[str] = None):
        """returns a string with a pretty table ready to be printed on a terminal.

        powered by :py:func:`humanfriendly.tables.format_pretty_table`
        """
        columns, rows = self.get_table_colums_and_rows(columns)
        return format_pretty_table(rows, columns)

    def validate_columns(self, columns):
        mismatched_columns = set(columns).difference(set(dir(self.model_class)))
        if not columns:
            columns = self.model_class.__visible_atttributes__

        elif mismatched_columns:
            raise ValueError(
                f'the following columns are not available '
                f'for {self.model_class}'
            )

    def to_dict(self) -> List[dict]:
        """calls ``.to_dict()`` in each children of this collection."""
        return [m.to_dict() for m in self]


class ModelList(list, IterableCollection):
    """Implementation of :py:class:`uiclasses.IterableCollection` with
    :py:class:`list`.

    """

    def __init__(self, model_class: type, children: List[Model]):
        self.initialize(model_class)
        if not isinstance(children, ITERABLES):
            raise TypeError(
                f"ModelList requires the 'children' attribute to be "
                f"a list, got {children!r} {type(children)} instead"
            )

        super().__init__(map(model_class, children))


class ModelSet(OrderedSet, IterableCollection):
    """Implementation of :py:class:`uiclasses.IterableCollection` with
    :py:class:`ordered_set.OrderedSet`.

    """

    def __init__(self, model_class: type, children: List[Model]):
        self.initialize(model_class)
        if not isinstance(children, ITERABLES):
            raise TypeError(
                f"ModelList requires the 'children' attribute to be "
                f"a list, got {children!r} {type(children)} instead"
            )

        super().__init__(map(model_class, children))
