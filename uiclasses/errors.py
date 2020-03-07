class UIClassesException(Exception):
    """base exception for anything raised within this python package
    """



class InexistentAttribute(UIClassesException):
    """raised when trying to access a key that is not present in a Model's
    __data__ property.  """
