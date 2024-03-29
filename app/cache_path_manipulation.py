# Copyright (C) 2022-2023 EZCampus 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Cache is used to manage internal temporary files made the on machine during runtime.

cache_id or similar verbiage is used to describe a cache key value used to identify specific use cases for each cached
file. For example, it might be the unique identifier for a user's generated ics file.
"""

from uuid import uuid4
import errno
import os

from constants import CACHE_DIR


def __ensure_file_path_exists(file_path: str):
    """Check if a file path exists, if not create it.

    Args:
        file_path: File path to ensure of existence.

    Raises:
        OSError: Not possible.
    """
    try:
        os.makedirs(file_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_cache_path(file_name: str, cache_id: str = None) -> str:
    """Get the cache path given a base file_name and an optional cache_id.

    Args:
        file_name: Base file name.
        cache_id: Used for identifying individual specific files.

    Returns:
        File path.
    """
    # Default a cache id if one does not exist or is invalid.
    if not isinstance(cache_id, str) or cache_id is None:
        cache_id = str(uuid4())

    __ensure_file_path_exists(CACHE_DIR)
    path, extension = os.path.splitext(file_name)
    combined_path = f"{CACHE_DIR}{path}{cache_id if isinstance(cache_id, str) else ''}{extension}"
    return combined_path


def remove_file_path(file_path: str):
    """Remove a file path

    Args:
        file_path: File path to remove.

    Raises:
        FileNotFoundError: File does not exist.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise FileNotFoundError(f"File path \"{file_path}\" does not exist!")
