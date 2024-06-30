import importlib
import importlib.machinery
import importlib.metadata
import importlib.resources
import importlib.simple
import importlib.util
import typing

import packaging.metadata
import packaging.requirements
import packaging.version
import toml
import typing_extensions
from result import Result
from result import as_result

from featlib._utils import read_file_res
from featlib._utils import toml_loads_res
from featlib.constants import PYPROJECT_FILE_NAME

OptionalDependencyTable: typing_extensions.TypeAlias = dict[
    str,
    list[packaging.requirements.Requirement],
]


def get_optional_dependencies_from_pyproject_file(
    path: str,
) -> Result[
    OptionalDependencyTable,
    OSError | toml.TomlDecodeError | TypeError | ValueError,
]:
    return read_file_res(path).and_then(get_optional_dependencies_from_string)


def get_optional_dependencies_from_string(
    source: str,
) -> Result[OptionalDependencyTable, toml.TomlDecodeError | TypeError | ValueError]:
    return toml_loads_res(source).and_then(get_optional_dependencies_from_toml_dict)


@as_result(ValueError)
def get_optional_dependencies_from_toml_dict(
    data: dict[str, typing.Any],
) -> OptionalDependencyTable:
    if "project" not in data:
        raise ValueError(f"malformed {PYPROJECT_FILE_NAME}: no `project` key")

    project: dict[str, typing.Any] = data["project"]

    if "optional-dependencies" not in project:
        return {}

    return {
        feature_name: list(map(packaging.requirements.Requirement, raw_dependencies))
        for feature_name, raw_dependencies in project["optional-dependencies"].items()
    }


def get_module_metadata(name: str) -> importlib.metadata.PackageMetadata | None:
    try:
        metadata = importlib.metadata.metadata(name)
    except importlib.metadata.PackageNotFoundError:
        return None
    else:
        return metadata


def is_module_available(requirement: packaging.requirements.Requirement) -> bool:
    metadata = get_module_metadata(requirement.name)

    if metadata is None:
        return False

    received_version_raw = metadata.get("Version")

    if received_version_raw is None:
        return False

    _received_version = packaging.version.parse(received_version_raw)

    return _received_version in requirement.specifier
