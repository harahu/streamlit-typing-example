import sys
import tempfile
from importlib.metadata import version

import streamlit as st
from mypy import api as mypy_api


def type_check(source: str) -> tuple[str, str, int]:
    """Wrapper around the mypy api that allows for type checking a string as if
      it were a python source file.

    :param source: The python source code to type-check.
    :return: a Tuple[str, str, int], namely (<normal_report>, <error_report>, <exit_status>),
      in which <normal_report> is what mypy normally writes to `sys.stdout`, <error_report>
      is what mypy normally writes to `sys.stderr` and exit_status is the exit status
      mypy normally returns to the operating system.
    """
    with tempfile.TemporaryDirectory() as tmpdir_name:
        with open(f"{tmpdir_name}/_source.py", "w") as f:
            f.write(source)

        normal_report, error_report, exit_status = mypy_api.run(
            [f"{tmpdir_name}/_source.py"]
        )

    normal_report = normal_report.removesuffix(" in 1 file (checked 1 source file)\n")

    normal_report = "\n".join(
        line.removeprefix(f"{tmpdir_name}/_source.py:")
        for line in normal_report.splitlines()
    )

    return normal_report, error_report, exit_status


def render_buffer(buffer: list[str], kind: str) -> list[str]:
    buffer_text = "\n\n".join(buffer)
    if buffer_text:
        if kind == "note":
            st.info(buffer_text)
        else:
            st.error(buffer_text)

    return []


def render_normal_report(report: str) -> None:
    lines = report.splitlines()

    if lines:
        last_line = lines[-1]

        if last_line.startswith("Success"):
            st.success(last_line)
            lines = lines[:-1]
        elif last_line.startswith("Found"):
            st.error(last_line)
            lines = lines[:-1]

        buffer: list[str] = []
        last_line_number = "-1"
        last_line_kind = ""
        for line in lines:
            kind = "note" if "note: " in line else "error"
            line_number = line.split(":")[0]

            if last_line_number != line_number or last_line_kind != kind:
                buffer = render_buffer(buffer, last_line_kind)
                last_line_number = line_number
                last_line_kind = kind

            buffer.append(line)
        render_buffer(buffer, last_line_kind)


def main() -> None:
    st.sidebar.title("Streamlit Typing Playground")
    st.sidebar.write(
        "A tool for quickly checking how mypy evaluates snippets of streamlit "
        "code, without having to install mypy."
    )

    st.sidebar.write(
        "Inspired by [Mypy Playground](https://mypy-play.net/), but a lot more "
        "opinionated, as you cannot change any settings."
    )

    st.sidebar.caption(
        "python"
        f" v{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        "<br/>"
        f"mypy v{version('mypy')}"
        "<br/>"
        f"streamlit v{version('streamlit')}",
        unsafe_allow_html=True,
    )

    source = st.text_area(
        label="Python Source Code",
        label_visibility="collapsed",
        height=500,
        max_chars=1000,
        placeholder=""""Please paste some streamlit-related code into this textbox. E.g.:

import streamlit as st

option = st.select_slider(
    label="Make a choice",
    options=["foo", "bar", "baz"],
)

reveal_type(option)
        """,
    )

    if source:
        normal_report, error_report, exit_status = type_check(source=source)
        render_normal_report(normal_report)


if __name__ == "__main__":
    main()
