#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import asyncio
import copy
import dataclasses
import json
import os
import subprocess
from datetime import datetime
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import yaml
from aiostream import stream
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.models import Type as MessageType
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@dataclasses.dataclass
class Message:
    prefix: str
    message: AirbyteMessage


@dataclasses.dataclass
class StreamStats:
    stream: str
    record_count = 0

    columns_to_diff_count: dict[str, int]
    columns_to_right_missing: dict[str, int]
    columns_to_left_missing: dict[str, int]
    columns_to_equal: dict[str, int]

    left_rows_missing: dict[str, int]
    right_rows_missing: dict[str, int]
    mismatch: list
    fields_to_ignore: set
    unmatched_left_no_pk: list
    unmatched_right_no_pk: list
    min_date_left: Optional[str] = None
    max_date_left: Optional[str] = None
    min_date_right: Optional[str] = None
    max_date_right: Optional[str] = None

    def __repr__(self):
        return f"StreamStats({vars(self)})"


async def compute_stream(
    connector,
    connector_version_left,
    connector_version_right,
    config_path,
    stream: AirbyteStream,
    stream_to_stream_config,
    streams_to_dataframe,
    streams_stats,
):
    print(f"running for {stream.name}")
    configured_catalog = _configured_catalog([stream])
    os.remove(f"secrets/tmp_catalog.json")
    with open(f"secrets/tmp_catalog.json", "w") as f:
        f.write(_configured_catalog([stream]).json(exclude_unset=True))
    command_left = f"docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/{connector}:{connector_version_left} read --config /{config_path} --catalog /secrets/tmp_catalog.json"
    command_right = f"docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/{connector}:{connector_version_right} read --config /{config_path} --catalog /secrets/tmp_catalog.json"

    configured_stream = configured_catalog.streams[0]
    cursor_field = configured_stream.cursor_field
    if cursor_field:
        cursor_field = cursor_field[0]

    subprocess_left = run_subprocess(command_left, "left")
    subprocess_right = run_subprocess(command_right, "right")

    streams_stats[stream.name] = StreamStats(stream.name, {}, {}, {}, {}, {}, {}, [], set(), [], [])
    streams_stats[stream.name].fields_to_ignore = set(stream_to_stream_config[stream.name].get("ignore_fields", []))
    for c in configured_stream.stream.json_schema["properties"].keys():
        streams_stats[stream.name].columns_to_diff_count[c] = 0
        streams_stats[stream.name].columns_to_right_missing[c] = 0
        streams_stats[stream.name].columns_to_left_missing[c] = 0
        streams_stats[stream.name].columns_to_equal[c] = 0

    while subprocess_left.__anext__() and subprocess_right.__anext__():
        try:
            left = await subprocess_left.__anext__()
            right = await subprocess_right.__anext__()

            if left.message.type != right.message.type:
                print(f"Type mismatch: {left.message.type} != {right.message.type}")
                print(left)
                print()
                print(right)
                print(left.message.type == right.message.type)
                return
            if left.message.type != MessageType.RECORD:
                continue
            else:
                assert left.message.record.stream == right.message.record.stream
                stream_stats = streams_stats[left.message.record.stream]

                stream_stats.record_count += 1

                if cursor_field:
                    if stream_stats.min_date_left is None:
                        stream_stats.min_date_left = left.message.record.data[cursor_field]
                    if stream_stats.max_date_left is None:
                        stream_stats.max_date_left = left.message.record.data[cursor_field]
                    stream_stats.min_date_left = min(stream_stats.min_date_left, left.message.record.data[cursor_field])
                    stream_stats.max_date_left = max(stream_stats.max_date_left, left.message.record.data[cursor_field])
                    if stream_stats.min_date_right is None:
                        stream_stats.min_date_right = right.message.record.data[cursor_field]
                    if stream_stats.max_date_right is None:
                        stream_stats.max_date_right = right.message.record.data[cursor_field]
                    stream_stats.min_date_right = min(stream_stats.min_date_right, right.message.record.data[cursor_field])
                    stream_stats.max_date_right = max(stream_stats.max_date_right, right.message.record.data[cursor_field])

                # configured_stream: ConfiguredAirbyteStream = [stream for stream in configured_catalog.streams if stream.stream.name == left.message.record.stream][0]
                primary_key = configured_stream.primary_key
                if primary_key:
                    primary_key = primary_key[0][0]

                if primary_key:
                    if left.message.record.data[primary_key] != right.message.record.data[primary_key]:
                        stream_stats.left_rows_missing[left.message.record.data[primary_key]] = left

                        right_stream_stats = streams_stats[right.message.record.stream]
                        right_stream_stats.right_rows_missing[right.message.record.data[primary_key]] = right
                        print(f"stream: {left.message.record.stream} and {right.message.record.stream}")
                        print(f"left: {left.message.record.data}")
                        print(f"right: {right.message.record.data}")
                        continue
                    else:
                        compare_records(left, right, stream_stats)
                        stream_stats.record_count += 1
                else:
                    # compare_records(left, right, stream_stats)
                    left_data_clone = copy.deepcopy(left.message.record.data)
                    right_data_clone = copy.deepcopy(right.message.record.data)
                    print(f"ignore fields: {stream_stats.fields_to_ignore}")
                    for field in stream_stats.fields_to_ignore:
                        left_data_clone.pop(field, None)
                        right_data_clone.pop(field, None)
                    print(f"left: {left_data_clone}")
                    print(f"right: {right_data_clone}")
                    stream_stats.unmatched_left_no_pk.append(left_data_clone)
                    stream_stats.unmatched_right_no_pk.append(right_data_clone)

                if left.message.record.data != right.message.record.data:
                    print(f"Data mismatch: {left.message.record.data} != {right.message.record.data}")
                    stream_stats.mismatch.append((left, right))

                # check missing
                left_keys = set(stream_stats.left_rows_missing.keys())
                for left_key in left_keys:
                    print(f"missinh {left_key}")
                    if left_key in stream_stats.right_rows_missing:
                        print(f"found {left_key} in right")
                        compare_records(stream_stats.left_rows_missing[left_key], stream_stats.right_rows_missing[left_key], stream_stats)
                        stream_stats.left_rows_missing.pop(left_key)
                        stream_stats.right_rows_missing.pop(left_key)
                        stream_stats.record_count += 1
                    else:
                        print(f"did not find {left_key} in right")
        except StopAsyncIteration:
            print("stop async")
            pass
        finally:
            # FIXME needd to do another check of missing
            # check missing
            # FIXME this is copypasted
            primary_key = configured_stream.primary_key
            if primary_key:
                primary_key = primary_key[0][0]
            try:
                while subprocess_left.__anext__():
                    # FIXME need to handle case where there is no pk!
                    left = await subprocess_left.__anext__()
                    if left.message.type != MessageType.RECORD:
                        continue
                    if left.message.record.stream not in streams_stats:
                        streams_stats[left.message.record.stream] = StreamStats(
                            left.message.record.stream, {}, {}, {}, {}, {}, {}, [], set(), [], []
                        )
                        streams_stats[left.message.record.stream].fields_to_ignore = set(
                            stream_to_stream_config[left.message.record.stream].get("ignore_fields", [])
                        )
                    stream_stats = streams_stats[left.message.record.stream]
                    if cursor_field:
                        if stream_stats.min_date_left is None:
                            stream_stats.min_date_left = left.message.record.data[cursor_field]
                        if stream_stats.max_date_left is None:
                            stream_stats.max_date_left = left.message.record.data[cursor_field]
                        stream_stats.min_date_left = min(stream_stats.min_date_left, left.message.record.data[cursor_field])
                        stream_stats.max_date_left = max(stream_stats.max_date_left, left.message.record.data[cursor_field])
                    if primary_key:
                        stream_stats.left_rows_missing[left.message.record.data[primary_key]] = left
                    else:
                        # need to remove ignored fields?
                        for field in stream_stats.fields_to_ignore:
                            left.message.record.data.pop(field, None)
                        stream_stats.unmatched_left_no_pk.append(left.message.record.data)
            except StopAsyncIteration:
                pass
            try:
                while subprocess_right.__anext__():
                    right = await subprocess_right.__anext__()
                    if right.message.type != MessageType.RECORD:
                        continue
                    stream_stats = streams_stats[right.message.record.stream]
                    if cursor_field:
                        cursor_time = right.message.record.data.get(cursor_field)
                        if cursor_time:
                            if stream_stats.min_date_right is None:
                                stream_stats.min_date_right = cursor_time
                            if stream_stats.max_date_right is None:
                                stream_stats.max_date_right = cursor_time
                            stream_stats.min_date_right = min(stream_stats.min_date_right, cursor_time)
                            stream_stats.max_date_right = max(stream_stats.max_date_right, cursor_time)
                    if primary_key:
                        if right.message.record.data[primary_key] in stream_stats.left_rows_missing:
                            compare_records(stream_stats.left_rows_missing[right.message.record.data[primary_key]], right, stream_stats)
                            stream_stats.left_rows_missing.pop(right.message.record.data[primary_key])
                            stream_stats.record_count += 1
                        else:
                            stream_stats.right_rows_missing[right.message.record.data[primary_key]] = right
                    else:
                        # need to remove ignored fields?
                        for field in stream_stats.fields_to_ignore:
                            right.message.record.data.pop(field, None)
                        stream_stats.unmatched_right_no_pk.append(right.message.record.data)
            except StopAsyncIteration:
                pass
            for stream_name, stream_stats in streams_stats.items():
                print(f"stream: {stream_name}")
                print(configured_catalog)
                configured_streams = [stream for stream in configured_catalog.streams if stream.stream.name == stream_name]
                if len(configured_streams) == 0:
                    return
                configured_stream = configured_streams[0]
                if stream_name != configured_stream.stream.name:
                    continue
                primary_key = configured_stream.primary_key
                if primary_key:
                    left_keys = set(stream_stats.left_rows_missing.keys())
                    for left_key in left_keys:
                        print(f"missinh {left_key}")
                        if left_key in stream_stats.right_rows_missing:
                            print(f"found {left_key} in right")
                            compare_records(
                                stream_stats.left_rows_missing[left_key], stream_stats.right_rows_missing[left_key], stream_stats
                            )
                            stream_stats.record_count += 1
                            stream_stats.left_rows_missing.pop(left_key)
                            stream_stats.right_rows_missing.pop(left_key)
                        else:
                            print(f"did not find {left_key} in right")
                else:
                    # no pk
                    left_indices_to_remove = []
                    right_indices_to_remove = []
                    for left_index in range(len(stream_stats.unmatched_left_no_pk)):
                        left_data = stream_stats.unmatched_left_no_pk[left_index]
                        for right_index in range(len(stream_stats.unmatched_right_no_pk)):
                            right_data = stream_stats.unmatched_right_no_pk[right_index]
                            left_dump = json.dumps(left_data)
                            right_dump = json.dumps(right_data)
                            print(f"left: {left_dump}")
                            print(f"right: {right_dump}")
                            print(f"left == right: {left_dump == right_dump}")
                            if json.dumps(left_data) == json.dumps(right_data):
                                # stream_stats.unmatched_left_no_pk.pop(left_index)
                                # stream_stats.unmatched_right_no_pk.pop(right_index)
                                left_indices_to_remove.append(left_index)
                                right_indices_to_remove.append(right_index)

                                # FIXME this is sort of approximate
                                # because it assumes the two dicts are exactly ewqual
                                for c in left_data.keys():
                                    if c not in stream_stats.columns_to_equal:
                                        stream_stats.columns_to_equal[c] = 0
                                    stream_stats.columns_to_equal[c] += 1
                                stream_stats.record_count += 1
                                break
                    for index in sorted(left_indices_to_remove, reverse=True):
                        stream_stats.unmatched_left_no_pk.pop(index)
                    for index in sorted(right_indices_to_remove, reverse=True):
                        stream_stats.unmatched_right_no_pk.pop(index)
            # FIXME need to check if both are done
            break


async def main():
    connector = "source-stripe"
    config_path = "secrets/prod_config_recent_only.json"
    regression_config_path = "regression_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    execution_time = datetime.now()
    start_time = config["start_date"]
    with open(regression_config_path) as f:
        regression_config = yaml.safe_load(f)

    connector_version_left = regression_config["connector_version_left"]
    connector_version_right = regression_config["connector_version_right"]

    stream_configs = regression_config["streams"]
    stream_to_stream_config = {stream_config["name"]: stream_config for stream_config in stream_configs}
    stream_names = [stream_config["name"] for stream_config in stream_configs]
    # FIXME uses left for the discover. this is somewhat arbitrary
    discover_command = f"docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/{connector}:{connector_version_left} discover --config /{config_path}"
    discover_result = subprocess.run(discover_command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    discover_output = discover_result.stdout
    catalog = None
    for discover_line in discover_output.split("\n"):
        if "CATALOG" in discover_line:
            discover_message = AirbyteMessage.parse_raw(discover_line)
            catalog = discover_message.catalog
            break
    if not catalog:
        print(f"Could not find catalog in {discover_output}")
    streams = [stream for stream in catalog.streams if stream.name in stream_names]

    streams_stats = {}
    streams_to_dataframe = {}
    for stream in streams:
        print(f"processing stream {stream.name}")
        await compute_stream(
            connector,
            connector_version_left,
            connector_version_right,
            config_path,
            stream,
            stream_to_stream_config,
            streams_to_dataframe,
            streams_stats,
        )
        print(f"done processing stream {stream.name}")

    for stream_stats in streams_stats.values():
        stats_rows = []
        for column in stream_stats.columns_to_diff_count:
            stats_rows.append(
                {
                    "stream": stream_stats.stream,
                    "column": column,
                    "metric": "diff_count",
                    "value": stream_stats.columns_to_diff_count[column],
                }
            )
        for column in stream_stats.columns_to_equal:
            stats_rows.append(
                {
                    "stream": stream_stats.stream,
                    "column": column,
                    "metric": "equal_count",
                    "value": stream_stats.columns_to_equal[column],
                }
            )
        df = pd.DataFrame.from_records(stats_rows)
        streams_to_dataframe[stream_stats.stream] = df
        print(f"done processing {stream_stats.record_count} records")
        print(f"columns_to_diff_count: {stream_stats.columns_to_diff_count}")
        print(f"columns_to_right_missing: {stream_stats.columns_to_right_missing}")
        print(f"columns_to_left_missing: {stream_stats.columns_to_left_missing}")
        print(f"columns_to_equal: {stream_stats.columns_to_equal}")
        # NEED TO VERIFY BOTH ARE DONE

        print(f"left_rows_missing: {stream_stats.left_rows_missing}")
        print(len(stream_stats.left_rows_missing))

        print(f"right_rows_missing: {stream_stats.right_rows_missing}")
        print(len(stream_stats.right_rows_missing))

    generate_plots_single_pdf_per_metric(
        streams_to_dataframe, streams_stats, connector, connector_version_left, connector_version_right, start_time, execution_time
    )


def _configured_catalog(streams):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream,
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
                primary_key=stream.source_defined_primary_key,
                cursor_field=stream.default_cursor_field,
            )
            for stream in streams
        ]
    )


def generate_plots_single_pdf_per_metric(
    streams_to_dataframe,
    streams_stats,
    source_name,
    left_version,
    right_version,
    start_time,
    execution_time,
    output_filename="plots_combined_per_metric.pdf",
):
    # diff_pdf_filename = "diff.pdf"
    # diff_pdf = canvas.Canvas(diff_pdf_filename)
    diff_filename = "diff_{stream}.jsonl"
    with PdfPages(output_filename) as pdf:

        # Generate summary
        # TODO
        summary_stats = []
        for stream_name, stream_stat in streams_stats.items():
            any_diff = any(
                [
                    val > 0
                    for col, val in streams_stats[stream_name].columns_to_diff_count.items()
                    if col not in streams_stats[stream_name].fields_to_ignore
                ]
            )
            print(f"diff for stream {stream_name}: {streams_stats[stream_name].columns_to_diff_count}")
            print(f"stream stat for {stream_name}: {streams_stats[stream_name]}")
            stat = {
                "stream": stream_name,
                "OK": not any_diff
                and len(streams_stats[stream_name].left_rows_missing) == 0
                and len(streams_stats[stream_name].right_rows_missing) == 0,
                "diff_fields": sum([val for col, val in streams_stats[stream_name].columns_to_diff_count.items()]),
                "record_count": streams_stats[stream_name].record_count,
                "left_additional_records": len(streams_stats[stream_name].left_rows_missing)
                + len(streams_stats[stream_name].unmatched_left_no_pk),
                "right_additional_records": len(streams_stats[stream_name].right_rows_missing)
                + len(streams_stats[stream_name].unmatched_right_no_pk),
                "min_date_left": datetime.utcfromtimestamp(
                    streams_stats[stream_name].min_date_left,
                ).strftime("%Y-%m-%d %H:%M:%S")
                if streams_stats[stream_name].min_date_left
                else None,
                "max_date_left": datetime.utcfromtimestamp(
                    streams_stats[stream_name].max_date_left,
                ).strftime("%Y-%m-%d %H:%M:%S")
                if streams_stats[stream_name].max_date_left
                else None,
                "min_date_right": datetime.utcfromtimestamp(
                    streams_stats[stream_name].min_date_right,
                ).strftime("%Y-%m-%d %H:%M:%S")
                if streams_stats[stream_name].min_date_right
                else None,
                "max_date_right": datetime.utcfromtimestamp(
                    streams_stats[stream_name].max_date_right,
                ).strftime("%Y-%m-%d %H:%M:%S")
                if streams_stats[stream_name].max_date_right
                else None,
            }
            print(f"stat:{stat}")
            summary_stats.append(stat)

            with open(diff_filename.format(stream=stream_name), "w") as diff_file:
                for left, right in stream_stat.mismatch:
                    left_data_json = json.dumps({"left": left.message.record.data, "right": right.message.record.data})
                    diff_file.write(left_data_json)

        # diff_pdf.save()
        # print(f"Diff saved to {diff_pdf_filename}")
        print(f"summary_stats:{summary_stats}")
        summary_df = pd.DataFrame.from_records(summary_stats)
        print(summary_df)
        # table = pd.pivot_table(summary_df, index='stream', columns=['equal', "record_count", "missing_left", "missing_right"], aggfunc=len, fill_value=0)
        # table = pd.pivot_table(summary_df, index='stream', columns=["record_count"], aggfunc=len, fill_value=0)
        table = summary_df.pivot_table(
            values=[
                "OK",
                "record_count",
                "diff_fields",
                "left_additional_records",
                "right_additional_records",
                "min_date_left",
                "max_date_left",
                "min_date_right",
                "max_date_right",
            ],
            index="stream",
            aggfunc="first",
        )
        plt.figure(figsize=(6, 4))

        def summary_color_cells(table, row, col):
            value = table.loc[row, col]
            if col == "record_count" and value == 0:
                return "yellow"
            if col in ["left_additional_records", "right_additional_records"] and value > 0:
                return "red"
            if col == "OK":
                if value:
                    return "green"
                else:
                    return "red"
            return "white"  # Default color for other cells

        summary_cell_colors = [[summary_color_cells(table, row, col) for col in table.columns] for row in table.index]
        plt.table(cellText=table.values, colLabels=table.columns, rowLabels=table.index, loc="center", cellColours=summary_cell_colors)
        plt.title(
            f"Summary stats for {source_name}\nleft: {left_version} ---- right:{right_version}\nstart_time:{start_time}\nexecution_time:{execution_time}",
            y=2,
        )
        plt.axis("off")  # Hide axis
        pdf.savefig(bbox_inches="tight", pad_inches=1)
        plt.close()

        ordered_streams = sorted(streams_to_dataframe.keys())
        for stream in ordered_streams:
            group_data = streams_to_dataframe[stream]
            # for stream, group_data in streams_to_dataframe.items():
            # Generate per-stream tables
            print(f"group_data for stream {stream}\n{group_data}")
            table = pd.pivot_table(group_data, values="value", index="column", columns="metric")
            # Plotting table using matplotlib

            # Define a function to assign colors based on conditions
            print(f"stream: {stream}")
            print(f"fields_to_ignore: {streams_stats[stream].fields_to_ignore}")

            def color_cells(table, row, col):
                value = table.loc[row, col]
                if value > 0 and col != "equal_count":
                    s = table.loc[row].name
                    if s in streams_stats[stream].fields_to_ignore:
                        print(f"ignoring {s} for stream {stream}")
                        return "yellow"
                    else:
                        print(f"not ignoring {s} for stream {stream}")
                        return "red"
                return "white"  # Default color for other cells

            # Convert table data to a list for cell colors
            cell_colors = [[color_cells(table, row, col) for col in table.columns] for row in table.index]

            plt.figure(figsize=(6, 4))
            plt.title(f"Stream: {stream}", y=3.2)
            plt.table(cellText=table.values, colLabels=table.columns, rowLabels=table.index, cellColours=cell_colors, loc="center")
            plt.axis("off")  # Hide axis

            # Save the table as a page in the PDF
            pdf.savefig(bbox_inches="tight", pad_inches=1)
            plt.close()

        for stream, group_data in streams_to_dataframe.items():
            grouped = group_data.groupby("column")
            for column, group_data in grouped:
                # Create a table for each stream and column combination
                table = pd.pivot_table(group_data, values="value", index="metric", columns="column")

                # Plotting table using matplotlib
                plt.figure(figsize=(6, 4))
                plt.table(cellText=table.values, colLabels=table.columns, rowLabels=table.index, loc="center")
                plt.title(f"Stream: {stream}, Column: {column}")
                plt.axis("off")  # Hide axis

                # Save the table as a page in the PDF
                pdf.savefig(bbox_inches="tight", pad_inches=1)
                plt.close()

        print(f"Tables saved to {output_filename}")


def compare_records(left, right, stream_stats):
    for column, left_value in left.message.record.data.items():
        if column not in stream_stats.columns_to_diff_count:
            stream_stats.columns_to_diff_count[column] = 0
        if column not in stream_stats.columns_to_right_missing:
            stream_stats.columns_to_right_missing[column] = 0
        if column not in stream_stats.columns_to_left_missing:
            stream_stats.columns_to_left_missing[column] = 0
        if column not in stream_stats.columns_to_equal:
            stream_stats.columns_to_equal[column] = 0

        if column not in right.message.record.data:
            stream_stats.columns_to_right_missing[column] += 1
            continue
        elif left_value != right.message.record.data[column]:
            stream_stats.columns_to_diff_count[column] += 1
        else:
            stream_stats.columns_to_equal[column] += 1
    for column, right_value in right.message.record.data.items():
        if column not in stream_stats.columns_to_diff_count:
            stream_stats.columns_to_diff_count[column] = 0
        if column not in stream_stats.columns_to_right_missing:
            stream_stats.columns_to_right_missing[column] = 0
        if column not in stream_stats.columns_to_left_missing:
            stream_stats.columns_to_left_missing[column] = 0
        if column not in stream_stats.columns_to_equal:
            stream_stats.columns_to_equal[column] = 0
        if column not in left.message.record.data:
            stream_stats.columns_to_left_missing[column] += 1


async def is_next_item_available(generator):
    async for _ in asyncio.as_completed([generator.__anext__()]):
        return True


async def run_subprocess(command, suffix):
    # Create a subprocess
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

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
