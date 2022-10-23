import streamlit  # noqa: F401
from pytest_mock import MockerFixture

from typing_playground.playground import (main, maybe_render_report_header,
                                          type_check)


class TestTypeCheck:
    def test_empty(self) -> None:
        n, e, c = type_check(source="")
        assert n == "Success: no issues found in 1 source file"
        assert e == ""
        assert c == 0

    def test_legal(self) -> None:
        n, e, c = type_check(source="foo: int = 42")
        assert n == "Success: no issues found in 1 source file"
        assert e == ""
        assert c == 0

    def test_legal_with_reveal(self) -> None:
        n, e, c = type_check(source="foo: int = 42\nreveal_type(foo)")
        assert (
            n
            == '2: note: Revealed type is "builtins.int"\n'
            "Success: no issues found in 1 source file"
        )
        assert e == ""
        assert c == 1

    def test_illegal(self) -> None:
        n, e, c = type_check(source="foo: int = None")
        assert (
            n
            == '1: error: Incompatible types in assignment (expression has type "None",'
            ' variable has type "int")\nFound 1 error'
        )
        assert e == ""
        assert c == 1

    def test_illegal_with_reveal(self) -> None:
        n, e, c = type_check(source="foo: str = 42\nreveal_type(foo)")
        assert (
            n
            == '1: error: Incompatible types in assignment (expression has type "int",'
            ' variable has type "str")\n2: note: Revealed type is'
            ' "builtins.str"\nFound 1 error'
        )
        assert e == ""
        assert c == 1


class TestMaybeRenderReportHeader:
    def test_recognized_error(self) -> None:
        assert maybe_render_report_header("Found 1 error")

    def test_recognized_success(self) -> None:
        assert maybe_render_report_header("Success: no issues found in 1 source file")

    def test_unrecognized(self) -> None:
        assert not maybe_render_report_header("I like pizza")


class TestMain:
    def test(self) -> None:
        main()

    def test_with_legal_input(self, mocker: MockerFixture) -> None:
        mocker.patch(
            target="streamlit.text_area",
            return_value="foo: int = 42",
        )

        mocker.patch(
            target="streamlit.button",
            return_value=True,
        )

        main()

    def test_with_illegal_input(self, mocker: MockerFixture) -> None:
        mocker.patch(
            target="streamlit.text_area",
            return_value="foo: str = 42",
        )

        mocker.patch(
            target="streamlit.button",
            return_value=True,
        )

        main()
