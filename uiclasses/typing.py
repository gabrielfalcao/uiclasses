from typing import NewType
from uiclasses import base
from uiclasses import collections


Model = NewType("Model", base.Model)
ModelSet = NewType("ModelSet", collections.ModelSet)
ModelList = NewType("ModelList", collections.ModelList)

IterableCollection = NewType(
    "IterableCollection", collections.IterableCollection)
