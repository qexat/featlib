"""
This module contains the code that handles the registration of optional
dependencies when `featlib` is first imported.
"""

import inspect
import os.path
import sys

from result import Err, Ok, Result

from featlib.constants import PYPROJECT_FILE_NAME
import featlib.dependencies


def get_project_root_path() -> str:
    """
    Return the path of the project root directory.

    Based on https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure/62510836#62510836
    """

    # stack trace history related to the call of this function
    frame_stack = inspect.stack()

    # get info about the module that has invoked this function
    # (index=0 is always this very module, index=1 is fine as long this function is not called by some other
    # function in this module)
    frame_info = frame_stack[1]

    # if there are multiple calls in the stacktrace of this very module, we have to skip those and take the first
    # one which comes from another module
    if frame_info.filename == __file__:
        for frame in frame_stack:
            if frame.filename != __file__:
                frame_info = frame
                break

    # path of the module that has invoked this function
    caller_path = frame_info.filename

    # absolute path of the of the module that has invoked this function
    caller_absolute_path = os.path.abspath(caller_path)

    # get the top most directory path which contains the invoker module
    paths = [p for p in sys.path if p in caller_absolute_path]
    paths.sort(key=len)

    return paths[0]


def get_pyproject_path() -> Result[str, OSError]:
    root_directory = get_project_root_path()
    path = os.path.join(root_directory, PYPROJECT_FILE_NAME)

    if not os.path.exists(path):
        return Err(FileNotFoundError(f"{PYPROJECT_FILE_NAME} file not found"))

    return Ok(path)


def get_optional_dependencies() -> featlib.dependencies.OptionalDependencyTable:
    match get_pyproject_path().and_then(
        featlib.dependencies.get_optional_dependencies_from_pyproject_file,
    ):
        case Ok(optional_dependencies):
            return optional_dependencies
        case Err(exception):
            raise exception


if __name__ != "__main__":
    pass
