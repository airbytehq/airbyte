import requests
import time
from enum import Enum


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    DONE = "done"


class ArsenkinTask:
    """Base task for Arsenkin"""

    url_base: str = "https://arsenkin.ru/tools/api/task/"

    def __init__(
            self,
            token: str,
            request_params: dict[str, any]
    ):
        self._token: str = token
        self._request_params: dict[str, any] = request_params
        self._task_id: str | None = None

        self._status: str = TaskStatus.NOT_STARTED
        self._result: dict[str, any] | None = None

    @property
    def result(self) -> dict[str, any]:
        return self._result

    def start(self) -> None:
        """Start task"""
        resp = requests.get(self.url_base + "set", params=self._request_params)
        if resp.status_code != 200:
            self._status = TaskStatus.FAILED
        else:
            self._task_id = resp.json()["task_id"]
            self._status = TaskStatus.IN_PROGRESS

    def get_status(self) -> TaskStatus:
        """Get status of this task"""
        if not self._task_id:
            raise ValueError  # TODO

        resp = requests.get(self.url_base + "check", params={"token": self._token, "task_id": self._task_id})
        task_status = resp.json()["status"]
        self._status = TaskStatus.DONE if task_status == "Done" else TaskStatus.IN_PROGRESS
        return self._status

    def wait_until_completed(self) -> None:
        """Wait until task is completed"""
        while True:
            status = self.get_status()
            if status == TaskStatus.DONE:
                resp = requests.get(self.url_base + "result", params={"token": self._token, "task_id": self._task_id})
                self._result = resp
                return
            elif status == TaskStatus.IN_PROGRESS:
                time.sleep(10)
            else:
                raise ValueError  # TODO

