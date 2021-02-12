import subprocess


def graceful_wait(process: subprocess.Popen, timeout_seconds: int):
    try:
        process.wait(timeout=timeout_seconds)
        return True
    except subprocess.TimeoutExpired as e:
        return False
