import tempfile

import streamlit as st
from mypy import api as mypy_api

source = st.text_area(label="Python Source Code")

with tempfile.TemporaryDirectory() as tmpdir_name:
    with open(f"{tmpdir_name}/_source.py", "w") as f:
        f.write(source)

    normal_report, error_report, exit_status = mypy_api.run(
        [f"{tmpdir_name}/_source.py"]
    )

if exit_status == 0:
    if normal_report:
        st.info(normal_report)
else:
    if normal_report:
        report = normal_report.removesuffix(" in 1 file (checked 1 source file)\n")
        for line in report.splitlines():
            st.error(line.removeprefix(f"{tmpdir_name}/_source.py:"))

if error_report:
    st.error(error_report)
