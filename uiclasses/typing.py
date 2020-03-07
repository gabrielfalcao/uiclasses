from typing import NewType
from .base import Model
from .collections import ModelSet
from .collections import ModelList


Model = NewType("Model", Model)
ModelSet = NewType("ModelSet", ModelSet)
ModelList = NewType("ModelList", ModelList)
