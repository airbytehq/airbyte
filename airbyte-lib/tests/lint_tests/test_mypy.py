import subprocess
import pytest

XFAIL = True # Toggle to set if the test is expected to fail or not

@pytest.mark.xfail(
    condition=XFAIL,
    reason=(
        "This is expected to fail until MyPy cleanup is completed.\n"
        "In the meanwhile, use `poetry run mypy .` to find and fix issues."
    )
)
def test_mypy_typing():
    # Run the check command
    check_result = subprocess.run(
        ["poetry", "run", "mypy", "."],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Assert that the Ruff command exited without errors (exit code 0)
    assert check_result.returncode == 0, \
        "MyPy checks failed:\n" + \
        f"{check_result.stdout.decode()}\n{check_result.stderr.decode()}\n\n" + \
        "Run `poetry run mypy .` to see all failures."
