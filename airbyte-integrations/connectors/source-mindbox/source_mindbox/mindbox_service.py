import time
from logging import Logger
from typing import Any, List, TypedDict

import requests


class OperationTaskNotStartedError(Exception):
    pass


class OperationTaskUpdateStatusError(Exception):
    pass


class ExportResult(TypedDict):
    processingStatus: str
    urls: List[str]


class OperationTaskStatus(TypedDict):
    export_id: str
    operation: str
    status: str
    exportResult: ExportResult
    status: str


class MindboxService:
    mindbox_base_url = "https://api.mindbox.ru/v3/"

    def __init__(self, endpoint_id: str, secret_key: str, logger: Logger):
        self._endpoint_id = endpoint_id
        self._secret_key = secret_key
        self._operations_tasks: dict[str, dict] = {}
        self._logger = logger

    def _api_call(self, path: str, params: dict[str, Any], json_payload: dict[Any, Any] = None) -> requests.Response:
        return requests.post(
            f"{self.mindbox_base_url}{path}",
            params=params,
            json=json_payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "Authorization": f'Mindbox secretKey="{self._secret_key}"',
            },
        )

    def start_operation_task(self, operation: str, json_payload: dict[str, Any] = {}) -> OperationTaskStatus:
        self._logger.info(f"Start operation {operation} export, json_payload: {json_payload}")
        status = self._api_call(
            "operations/sync",
            {
                "endpointId": self._endpoint_id,
                "operation": operation,
            },
            json_payload=json_payload,
        ).json()
        self._operations_tasks[status["exportId"]] = status
        return status

    def update_operation_task_status(self, operation: str, export_id: str) -> OperationTaskStatus:
        if export_id not in self._operations_tasks.keys():
            raise OperationTaskNotStartedError(f"{{operation: {operation}, export_id: {export_id}}} not started")
        status = self._api_call(
            "operations/sync",
            {
                "endpointId": self._endpoint_id,
                "operation": operation,
            },
            json_payload={"exportId": export_id},
        ).json()
        self._operations_tasks[export_id] = {**self._operations_tasks[export_id], **status}
        return self._operations_tasks[export_id]

    def wait_operation_task_succeeded(self, operation: str, export_id: str, wait_seconds: int = 5) -> OperationTaskStatus:
        while True:
            current_task_status = self.update_operation_task_status(operation=operation, export_id=export_id)
            processing_status = current_task_status["exportResult"]["processingStatus"]
            if processing_status == "Ready":
                self._operations_tasks[export_id] = {**self._operations_tasks[export_id], **current_task_status}
                self._logger.info(f"Export {export_id} (operation {operation}) status: Ready")
                return self._operations_tasks[export_id]
            elif processing_status == "NotReady":
                self._operations_tasks[export_id] = {**self._operations_tasks[export_id], **current_task_status}
                self._logger.info(f"Export {export_id} (operation {operation}) status: NotReady. Sleep for {wait_seconds} seconds")
                time.sleep(wait_seconds)
            else:
                raise OperationTaskUpdateStatusError(str(current_task_status))
