from __future__ import annotations

import collections
import collections.abc
import copy
import dataclasses
import functools
import typing

import packaging
import packaging.requirements

from .constants import PYPROJECT_FILE_NAME
from .dependencies import OptionalDependencyTable, is_module_available
import featlib.register


_P = typing.ParamSpec("_P")
_R = typing.TypeVar("_R")


class _GlobalDependencyTable:
    def __init__(self) -> None:
        self.__data: OptionalDependencyTable | None = None

    def __contains__(self, feature_name: str, /) -> bool:
        return feature_name in self.data

    @functools.cached_property
    def data(self) -> OptionalDependencyTable:
        if self.__data is None:
            self.__data = featlib.register.get_optional_dependencies()

        return self.__data

    def force_fetch_data(self) -> None:
        self.__data = None
        _ = self.data

    def get_feature_dependencies(
        self,
        name: str,
    ) -> list[packaging.requirements.Requirement]:
        return self.data[name]

    def is_feature_detected(self, name: str) -> bool:
        if name not in self:
            return False

        dependencies = self.get_feature_dependencies(name)

        for dependency in dependencies:
            if not is_module_available(dependency):
                return False

        return True


GLOBAL_DEPENDENCY_TABLE = _GlobalDependencyTable()


def cache_optional_dependencies() -> None:
    GLOBAL_DEPENDENCY_TABLE.force_fetch_data()


class UnavailableFeature(TypeError):
    @classmethod
    def from_calling_gatekept_function(
        cls, function_name: str, feature_name: str
    ) -> typing.Self:
        return cls(
            f"failed to call function {function_name!r}, as it is "
            f"gatekept behind feature {feature_name!r} which is not detected"
        )


class GatekeptFunction(typing.Generic[_P, _R]):
    def __init__(
        self,
        feature: Feature,
        function: collections.abc.Callable[_P, _R],
        fallback: collections.abc.Callable[_P, _R] | None = None,
    ) -> None:
        self.feature: typing.Final = feature
        self.function: typing.Final = function
        self.__fallback: collections.abc.Callable[_P, _R] | None = fallback

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        called = self.function if self.feature.is_available() else self.__fallback

        if called is None:
            raise UnavailableFeature.from_calling_gatekept_function(
                self.function.__name__,
                self.feature.name,
            )

        return called(*args, **kwargs)

    @property
    def name(self) -> str:
        return self.function.__name__

    def set_fallback(
        self,
        function: collections.abc.Callable[_P, _R],
        /,
    ) -> collections.abc.Callable[_P, _R]:
        self.__fallback = functools.wraps(self.function)(function)

        return function


@dataclasses.dataclass(slots=True)
class Feature:
    name: str

    def is_available(self) -> bool:
        return GLOBAL_DEPENDENCY_TABLE.is_feature_detected(self.name)

    def gatekeep(
        self,
        function: collections.abc.Callable[_P, _R],
        /,
    ) -> GatekeptFunction[_P, _R]:
        return GatekeptFunction(self, function)


def get_feature(name: str) -> Feature:
    if name not in GLOBAL_DEPENDENCY_TABLE.data:
        raise ValueError(f"feature {name!r} not found in {PYPROJECT_FILE_NAME}")

    return Feature(name)
