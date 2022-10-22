import sys
import tempfile
from importlib.metadata import version

import streamlit as st
from mypy import api as mypy_api


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


def render_buffer(buffer: list[str], kind: str, n: str) -> list[str]:
    if buffer:
        render_fn = st.info if kind == "note" else st.error

        buffer_text = f"Line {n}:  \n"
        buffer_text = buffer_text + "  \n".join(
            [f"- {l.removeprefix(f'{n}:')}" for l in buffer]
        )
        if buffer_text:
            render_fn(buffer_text)

    return []


def render_normal_report(report: str) -> None:
    lines = report.splitlines()

    if lines:
        last_line = lines[-1]

        if last_line.startswith("Success"):
            st.success(body=last_line, icon="🥳")
            lines = lines[:-1]
        elif last_line.startswith("Found"):
            st.error(body=last_line, icon="🚫")
            lines = lines[:-1]

        buffer: list[str] = []
        last_line_number = "-1"
        last_line_kind = ""
        for line in lines:
            kind = "note" if "note: " in line else "error"
            line_number = line.split(":")[0]

            if last_line_number != line_number or last_line_kind != kind:
                buffer = render_buffer(buffer, last_line_kind, last_line_number)
                last_line_number = line_number
                last_line_kind = kind

            buffer.append(line)
        render_buffer(buffer, last_line_kind, last_line_number)


def render_documentation() -> None:
    st.sidebar.title("Streamlit Typing Playground")
    st.sidebar.write(
        "A tool for quickly checking how mypy evaluates snippets of streamlit "
        "code, without having to install mypy.  \n\n"
        "Inspired by [Mypy Playground](https://mypy-play.net/), but a lot more "
        "opinionated, as you cannot change any settings."
    )

    st.sidebar.caption(
        "python"
        f" v{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} "
        f" \nmypy v{version('mypy')}  \nstreamlit v{version('streamlit')}",
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
        normal_report, error_report, exit_status = type_check(source=source)
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
