import asyncio
import dataclasses
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type as MessageType
)

from aiostream import stream

@dataclasses.dataclass
class Message:
    prefix: str
    message: AirbyteMessage



async def main():
    connector = "source-stripe"
    connector_version = "4.5.4"
    config_path = "secrets/config.json"
    command = f"docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/{connector}:{connector_version} read --config /{config_path} --catalog /secrets/tmp_catalog.json"

    subprocess_left = run_subprocess(command, "left")
    subprocess_right = run_subprocess(command, "right")

    record_count = 0

    columns_to_diff_count = {}
    columns_to_right_missing = {}
    columns_to_left_missing = {}
    columns_to_equal = {}

    while subprocess_left.__anext__() and subprocess_right.__anext__():
        try:
            left = await subprocess_left.__anext__()
            right = await subprocess_right.__anext__()

            record_count += 1

            if left.message.type != right.message.type:
                print(f"Type mismatch: {left.message.type} != {right.message.type}")
                print(left)
                print()
                print(right)
                print(left.message.type == right.message.type)
                return
            if left.message.type == MessageType.RECORD:
                for column, left_value in left.message.record.data.items():
                    if column not in columns_to_diff_count:
                        columns_to_diff_count[column] = 0
                    if column not in columns_to_right_missing:
                        columns_to_right_missing[column] = 0
                    if column not in columns_to_left_missing:
                        columns_to_left_missing[column] = 0
                    if column not in columns_to_equal:
                        columns_to_equal[column] = 0

                    if column not in right.message.record.data:
                        columns_to_right_missing[column] += 1
                        continue
                    elif left_value != right.message.record.data[column]:
                        columns_to_diff_count[column] += 1
                    else:
                        columns_to_equal[column] += 1
                for column, right_value in right.message.record.data.items():
                    if column not in columns_to_diff_count:
                        columns_to_diff_count[column] = 0
                    if column not in columns_to_right_missing:
                        columns_to_right_missing[column] = 0
                    if column not in columns_to_left_missing:
                        columns_to_left_missing[column] = 0
                    if column not in columns_to_equal:
                        columns_to_equal[column] = 0
                    if column not in left.message.record.data:
                        columns_to_left_missing[column] += 1

                if left.message.record.data != right.message.record.data:
                    print(f"Data mismatch: {left.message.record.data} != {right.message.record.data}")
        except StopAsyncIteration:
            print(f"done processing {record_count} records")
            print(f"columns_to_diff_count: {columns_to_diff_count}")
            print(f"columns_to_right_missing: {columns_to_right_missing}")
            print(f"columns_to_left_missing: {columns_to_left_missing}")
            print(f"columns_to_equal: {columns_to_equal}")
            # NEED TO VERIFY BOTH ARE DONE
            break

async def is_next_item_available(generator):
    async for _ in asyncio.as_completed([generator.__anext__()]):
        return True
async def run_subprocess(command, suffix):
    # Create a subprocess
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Read lines from stdout asynchronously
    async def read_lines(stream):
        async for line in stream:
            yield line.decode().rstrip()

    # Start reading lines from both stdout and stderr
    stdout_lines = read_lines(process.stdout)
    stderr_lines = read_lines(process.stderr)

    # Consume lines from both streams concurrently
    async for line in stdout_lines:
        yield Message(prefix=f"{suffix}: ", message=AirbyteMessage.parse_raw(line))

    # # Wait for the process to finish
    # await process.wait()

if __name__ == "__main__":
    asyncio.run(main())
