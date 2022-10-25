from os import PathLike, environ
import pathlib
import typing as T


Default = T.TypeVar("Default")
Cast = T.TypeVar("Cast")


def _get_path(__s_path: T.Optional[T.Union[str, PathLike]]) -> pathlib.Path:
    return (pathlib.Path(__s_path or "./") / ".env").resolve()


def _write_dotenv(
    io: T.IO[str], data: dict, use_quotes: bool, space_between_assignment: bool
):
    lines = []
    for key, value in data.items():
        lines.append(_create_str(key, value, use_quotes, space_between_assignment))
    print(*lines, sep="\n", file=io)


def _create_str(
    key: str, value: object, use_quotes: bool, space_between_assignment: bool
) -> str:
    if use_quotes and space_between_assignment:
        s = "{key} = '{value}'"
    elif use_quotes and not space_between_assignment:
        s = "{key}='{value}'"
    elif not use_quotes and space_between_assignment:
        s = "{key} = {value}"
    else:
        s = "{key}={value}"

    return s.format(key=key, value=value)


def _parse_dotenv(io: T.IO[str]):
    data = io.readlines()
    data_dict = {}
    for l in data:
        key, value = l.split("=")
        key, value = key.strip(), value.strip()
        if (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            value = (
                value.removeprefix("'")
                .removesuffix("'")
                .removeprefix('"')
                .removesuffix('"')
            )
        data_dict.update({key: value})
    return data_dict


def load_dotenv(
    env_path: T.Optional[T.Union[str, PathLike]] = None, override_env: bool = False
):
    path = _get_path(env_path)
    if path.is_file():
        with path.open("r") as env_file:
            data = _parse_dotenv(env_file)
            for key, value in data.items():
                if override_env and key in environ:
                    environ.update({key: value})
                elif override_env and not key in environ:
                    environ.update({key: value})
                elif not override_env and key in environ:
                    pass
                elif not override_env and not key in environ:
                    environ.update({key: value})
        return data
    else:
        raise FileNotFoundError(f"Unable to locate .env file in {str(path.parent)!r}")


@T.overload
def getenv(key: str) -> T.Optional[str]:
    ...


@T.overload
def getenv(key: str, *, default: Default = ...) -> T.Union[str, Default]:
    ...


@T.overload
def getenv(key: str, *, cast: T.Callable[[str], Cast] = ...) -> Cast:
    ...


@T.overload
def getenv(
    key: str, *, default: Default = ..., cast: T.Callable[[str], Cast] = ...
) -> Cast:
    ...


def getenv(
    key: str,
    default: T.Optional[T.Union[str, object]] = None,
    cast: T.Optional[T.Callable[..., object]] = None,
):
    value = environ.get(key, default)
    if cast:
        return cast(value)
    return value


def set_key(
    key: str,
    value: object,
    env_path: T.Optional[T.Union[str, PathLike]] = None,
    use_quotes: bool = True,
    space_assignment: bool = True,
    override_env: bool = False,
):
    path = _get_path(env_path)
    if path.is_file():
        with path.open() as env_load:
            data = _parse_dotenv(env_load)
        with path.open("w") as env_file:
            data.update({key: value})
            _write_dotenv(env_file, data, use_quotes, space_assignment)
            if override_env and key in environ:
                environ.update({key: str(value)})
            elif override_env and not key in environ:
                environ.update({key: str(value)})
            elif not override_env and key in environ:
                pass
            elif not override_env and not key in environ:
                environ.update({key: str(value)})
        return key, value
    else:
        raise FileNotFoundError(f"Unable to locate .env file in {str(path.parent)!r}")


def remove_key(
    key: str,
    env_path: T.Optional[T.Union[str, PathLike]] = None,
    override_env: bool = False,
    use_quotes: bool = True,
    space_assignment: bool = True,
):
    path = _get_path(env_path)
    if path.is_file():
        with path.open() as env_load:
            data = _parse_dotenv(env_load)
        value = data.pop(key, None)
        with path.open("w") as env_file:
            _write_dotenv(env_file, data, use_quotes, space_assignment)
        if override_env:
            environ.pop(key, None)
        return key, value
    else:
        raise FileNotFoundError(f"Unable to locate .env file in {str(path.parent)!r}")


class DotEnv:
    def __init__(
        self,
        env_path: T.Optional[T.Union[str, PathLike]] = None,
        use_quotes: bool = True,
        space_assignment: bool = True,
    ):
        self.__env_path = env_path
        self.__use_quotes = use_quotes
        self.__space_assignment = space_assignment

    def load(self, override_env: bool = False):
        return load_dotenv(self.__env_path, override_env)

    def set_key(self, key: str, value: object, override_env: bool = False):
        return set_key(
            key,
            value,
            self.__env_path,
            self.__use_quotes,
            self.__space_assignment,
            override_env,
        )

    def remove_key(self, key: str, override_env: bool = False):
        return remove_key(
            key,
            self.__env_path,
            override_env,
            self.__use_quotes,
            self.__space_assignment,
        )

    def getenv(
        self,
        key: str,
        default: T.Optional[Default] = None,
        cast: T.Optional[T.Callable[[str], Cast]] = None,
    ) -> T.Optional[T.Union[str, Default, Cast]]:
        return getenv(key, default=default, cast=cast)

    def update(
        self,
        new_path: T.Optional[T.Union[str, PathLike]] = None,
        use_quotes: bool = True,
        space_assignment: bool = True,
    ):
        """
        new_path: optional< str or PathLike > = default< current dir > // Where to search for the `.env` file
        use_quotes: bool = default< True > // Using quotes on values
        space_assignment: bool = default< True > // Using spaces between the assignment operator
        """
        self.__env_path = new_path
        self.__space_assignment = space_assignment
        self.__use_quotes = use_quotes

    @property
    def env_path(self):
        return _get_path(self.__env_path)


dotenv = DotEnv()


__all__ = ("load_dotenv", "set_key", "getenv", "dotenv")
__author__ = "waifusempire"
__version__ = "1.0.0"
__author_email__ = "waifusempire@gmail.com"
