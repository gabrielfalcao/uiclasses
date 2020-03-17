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
