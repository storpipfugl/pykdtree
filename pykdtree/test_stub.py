import os
import pytest

MYPY_TESTS_REQUIRED = os.environ.get("MYPY_TESTS_REQUIRED", None)


def import_stubtest():
    if MYPY_TESTS_REQUIRED:
        from mypy import stubtest

        return stubtest
    return pytest.importorskip("mypy.stubtest", reason="mypy is not installed")


def test_mypy(capsys):
    """
    Run mypy stub tests for pykdtree.
    This function checks for:
        - Type consistency in the stubs vs the definitions
        - Function / property signatures
        - Missing functions or properties in the stubs
    """
    stubtest = import_stubtest()
    code = stubtest.test_stubs(stubtest.parse_options(["pykdtree.kdtree"]))
    captured = capsys.readouterr()

    assert code == 0, "Mypy stub test failed:\n" + captured.out
