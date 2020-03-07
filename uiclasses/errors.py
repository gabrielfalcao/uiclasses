class UIClassesException(Exception):
    """base exception for anything raised within this python package
    """


class InexistentAttribute(UIClassesException):
    """raised when trying to access a key that is not present in a Model's
    __data__ property.  """


class InvalidJSON(UIClassesException):
    """raised when trying to parse a json string.

    raised by :py:meth:`~uiclasses.base.Model.from_json`.
    """
