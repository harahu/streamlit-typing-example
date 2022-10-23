import sys
import tempfile
from importlib.metadata import version
from typing import Final

import streamlit as st
from mypy import api as mypy_api

APP_TITLE: Final = "Streamlit Typing Playground"

NOTE_CUE: Final = "note"
ERROR_CUE: Final = "error"


def type_check(source: str) -> tuple[str, str, int]:
    """Type checks python code.

    Wrapper around the mypy api that allows for type checking a string as if
    it were a python source file.

    Parameters
    ----------
    source : str
        The python source code to type-check.

    Returns
    -------
    tuple[str, str, int]
        Return consists of (<normal_report>, <error_report>, <exit_status>),
        in which <normal_report> is what mypy normally writes to `sys.stdout`,
        <error_report> is what mypy normally writes to `sys.stderr` and
        <exit_status> is the exit status mypy normally returns to the operating
        system.

    """
    with tempfile.TemporaryDirectory() as tmpdir_name:
        with open(
            file=f"{tmpdir_name}/_source.py", mode="w", encoding="utf-8"
        ) as source_file:
            source_file.write(source)

        normal_report, error_report, exit_status = mypy_api.run(
            [f"{tmpdir_name}/_source.py"]
        )

    normal_report = normal_report.removesuffix(" in 1 file (checked 1 source file)\n")

    normal_report = "\n".join(
        line.removeprefix(f"{tmpdir_name}/_source.py:")
        for line in normal_report.splitlines()
    )

    return normal_report, error_report, exit_status


def render_buffer(buffer: list[str], kind: str, source_line_number: str) -> list[str]:
    if buffer:
        render_fn = st.info if kind == NOTE_CUE else st.error
        buffer_text = f"Line {source_line_number}:  \n" + "  \n".join(
            [f"- {line.removeprefix(f'{source_line_number}:')}" for line in buffer]
        )
        if buffer_text:
            render_fn(buffer_text)

    return []


def maybe_render_report_header(last_line: str) -> bool:
    if last_line.startswith("Success"):
        st.success(body=last_line, icon="🥳")
        return True
    if last_line.startswith("Found"):
        st.error(body=last_line, icon="🚫")
        return True
    return False


def render_normal_report(report: str) -> None:
    lines = report.splitlines()

    if lines:
        if maybe_render_report_header(last_line=lines[-1]):
            lines = lines[:-1]

        buffer: list[str] = []
        last_line_number = "-1"
        last_line_kind = ""
        for line in lines:
            kind = "note" if f"{NOTE_CUE}: " in line else "error"
            line_number = line.split(":")[0]

            if last_line_number != line_number or last_line_kind != kind:
                buffer = render_buffer(buffer, last_line_kind, last_line_number)
                last_line_number = line_number
                last_line_kind = kind

            buffer.append(line)
        render_buffer(buffer, last_line_kind, last_line_number)


def python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def render_documentation() -> None:
    st.sidebar.title(APP_TITLE)
    st.sidebar.write(
        "A tool for quickly checking how mypy evaluates snippets of streamlit "
        "code, without having to install mypy.  \n\n"
        "Inspired by [Mypy Playground](https://mypy-play.net/), but a lot more "
        "opinionated, as you cannot change any settings."
    )

    st.sidebar.caption(
        f"python v{python_version()}  \n"
        f"mypy v{version('mypy')}  \n"
        f"streamlit v{version('streamlit')}",
    )


def prompt_for_source() -> str:
    source = st.text_area(
        label="Python Source Code",
        label_visibility="collapsed",
        height=500,
        max_chars=1000,
        placeholder="""Please paste some streamlit-related code into this textbox. E.g.:

import streamlit as st

option = st.select_slider(
    label="Make a choice",
    options=["foo", "bar", "baz"],
)

reveal_type(option)
        """,
    )

    return source


def generate_and_render_report(source: str) -> None:
    with st.spinner(text="🔍 Digging in to those types..."):
        normal_report, _, _ = type_check(source=source)
        render_normal_report(normal_report)


def offer_type_checking() -> None:
    source = prompt_for_source()
    if st.button(
        label="Type-check with mypy",
        disabled=not source,
    ):
        generate_and_render_report(source=source)


def main() -> None:
    render_documentation()
    offer_type_checking()


if __name__ == "__main__":
    main()
