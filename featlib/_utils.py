import toml

from result import as_result


@as_result(FileNotFoundError, OSError)
def read_file_res(path: str, /) -> str:
    """
    Read a file given its `path`. Return a `Result`.
    """

    return open(path, "r").read()


toml_load_res = as_result(TypeError, toml.TomlDecodeError, FileNotFoundError)(toml.load)
toml_loads_res = as_result(TypeError, toml.TomlDecodeError)(toml.loads)
