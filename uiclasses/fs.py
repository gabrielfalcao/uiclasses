"""
runtime helper functions used for leveraging idiosyncrasies of testing.
"""
# pragma: nocover

import json
import logging
from typing import List
from pathlib import Path
from . import Model


logger = logging.getLogger(__name__)


def expanded_path(path: [str, Path]) -> Path:
    return Path(path).expanduser().absolute()


def store_models(items: List[Model], filename: str) -> bool:
    """helper method to store :py:class:`uiclasses.IterableCollection`
    instances serialized in json format and stored in the given
    filename.

    Very useful for command-line scripts that need to cache results of
    heavy API responses.

    """
    path = Path(filename)

    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open("w") as fd:
        json.dump(items.to_dict(), fd, indent=2)
        return True


def load_models(filename: str, model_class: Model) -> List[Model]:
    """helper function to load a  :py:class:`uiclasses.IterableCollection`
    from a file previously written by :py:func:`uiclasses.fs.store_models`.

    Very useful for command-line scripts that need to cache results of
    heavy API responses.
    """
    path = Path(filename)

    path.parent.mkdir(exist_ok=True, parents=True)
    if not path.exists():
        return None

    with path.open() as fd:
        try:
            items = json.load(fd)
        except json.decoder.JSONDecodeError as e:
            logger.warning(f"could not parse json from {filename}: {e}")
            return

        return model_class.List(items)
