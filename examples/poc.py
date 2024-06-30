# proof of concept of featlib

import featlib

FOO = featlib.get_feature("foo")


@FOO.gatekeep
def foo(string: str) -> None:
    import option

    print(option.Some(string))


@foo.set_fallback
def bar(string: str) -> None:
    print(string)


def main() -> None:
    foo("hello")


if __name__ == "__main__":
    main()
