from datetime import datetime
import os
import ujson
from threading import Lock, Thread
from typing import Any, Iterable, List, Mapping
from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from logging import getLogger
import pandas as pd
from typing import TYPE_CHECKING
from source_appmetrika_logs_stream_api.exceptions import UserDefinedSliceSkipException

from source_appmetrika_logs_stream_api.utils import filename_from_slice_window

if TYPE_CHECKING:
    from source_appmetrika_logs_stream_api.source import AppmetrikaLogsStreamApiStream, SourceAppmetrikaLogsStreamApi


logger = getLogger("airbyte")


class StreamWorkerThread(Thread):
    def __init__(
        self,
        stream_instance: "AppmetrikaLogsStreamApiStream",
        source_instance: "SourceAppmetrikaLogsStreamApi",
        thread_name: str,
        windows_to_load: list[Mapping[str, Any]],
        lock: Lock,
    ) -> None:
        Thread.__init__(self, name=thread_name, daemon=True)
        self.lock = lock
        self.stream_instance = stream_instance
        self.stream_class = stream_instance.__class__
        self.source_instance = source_instance
        self.thread_name = thread_name
        self.stream_instance.windows_to_load = windows_to_load
        self.records_count = 0
        self.is_running = True

    def process_stream_instanse_read(self):
        slices_count = 0
        slices_loaded = False
        try:
            slices = list(self.stream_instance.stream_slices())
            slices_loaded = True
            slices_count = len(slices)
            for slice_n, stream_slice in enumerate(slices, 1):
                window_datetime = datetime.fromtimestamp(stream_slice["window"]["stream_window_timestamp"])
                logger.info(f"Thread {self.thread_name}: Process window {window_datetime} [{slice_n}/{len(slices)} of thread windows]")
                try:
                    self.stream_instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
                except UserDefinedSliceSkipException as e:
                    logger.info(f"Skip slice {stream_slice} for status: {e}")
                    continue
                window = stream_slice["window"]
                filename = filename_from_slice_window(window)
                with open(filename, "r") as input_f:
                    df_reader = pd.read_csv(input_f, chunksize=50000)
                    for chunk in df_reader:
                        now_millis = int(datetime.now().timestamp() * 1000)
                        with self.lock:
                            print(
                                pd.DataFrame(
                                    [
                                        {
                                            "type": "RECORD",
                                            "record": {
                                                "stream": self.stream_instance.name,
                                                "data": data,
                                                "emitted_at": now_millis,
                                            },
                                        }
                                        for data in chunk.to_dict("records")
                                    ]
                                ).to_json(orient="records", lines=True)
                            )
                logger.info(f'Remove file {filename} for slice {datetime.fromtimestamp(window["stream_window_timestamp"])}')
                os.remove(filename)
        except AirbyteTracedException as e:
            raise e
        except Exception as e:
            logger.exception(f"Encountered an exception while reading stream {self.stream_instance.name} (Thread {self.thread_name})")
            display_message = self.stream_instance.get_error_display_message(e)
            if display_message:
                raise AirbyteTracedException.from_exception(e, message=display_message) from e
            raise e
        finally:
            if slices_loaded and slices_count == 0:
                logger.info(f"Finished syncing thread {self.thread_name} due to no stream slices was used.")
            else:
                logger.info(f"Finished syncing thread {self.thread_name}")
            self.is_running = False

    def run(self):
        logger.info(f"Start processing thread {self.name}")
        self.process_stream_instanse_read()
        self.is_running = False


class StreamWorkerThreadController:
    def __init__(
        self,
        source_instance: "SourceAppmetrikaLogsStreamApi",
        all_windows: list[Mapping[str, Any]],
        every_thread_kwargs: Mapping[str, Any],
        main_stream_instance: "AppmetrikaLogsStreamApiStream",
        multithreading_threads_count: int = 10,
    ):
        self.threads: List[StreamWorkerThread] = []
        self.main_stream_instance = main_stream_instance
        self.source_instance = source_instance
        self.lock = Lock()

        for i in range(multithreading_threads_count):
            self.threads.append(
                StreamWorkerThread(
                    stream_instance=self.main_stream_instance.__class__(
                        **every_thread_kwargs, data_type=self.main_stream_instance.data_type
                    ),
                    source_instance=self.source_instance,
                    thread_name=f"StreamThread-{self.main_stream_instance.name}-{i}",
                    windows_to_load=[],
                    lock=self.lock,
                )
            )
        while all_windows:
            for thread in self.threads:
                try:
                    thread.stream_instance.windows_to_load.append(all_windows.pop())
                except IndexError:
                    break

        self.records_count = 0

    @property
    def current_records_count(self):
        return sum([thread.records_count for thread in self.threads])

    @property
    def is_running(self) -> bool:
        return any([thread.is_running for thread in self.threads])

    def start_threads(self) -> None:
        for thread in self.threads:
            thread.start()

    def wait_until_threads_completed(self):
        while self.is_running:
            pass
        logger.info(f"All threads for stream '{self.main_stream_instance.name}' completed.")
