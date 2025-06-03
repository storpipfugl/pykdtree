import os
from contextlib import redirect_stdout
from io import StringIO
import pytest

MYPY_TESTS_REQUIRED = os.environ.get("MYPY_TESTS_REQUIRED", None)


def import_mypy():
    if MYPY_TESTS_REQUIRED:
        import mypy

        return mypy
    return pytest.importorskip("mypy", reason="mypy is not installed")


def test_mypy():
    """
    Run mypy stub tests for pykdtree.
    This function checks for:
        - Type consistency in the stubs vs the definitions
        - Function / property signatures
        - Missing functions or properties in the stubs
    """
    mypy = import_mypy()
    stubtest = mypy.stubtest

    out = StringIO()
    with redirect_stdout(out):
        code = stubtest.test_stubs(stubtest.parse_options(["pykdtree.kdtree"]))

    assert code == 0, "Mypy stub test failed:\n" + out.getvalue()


test_mypy()
