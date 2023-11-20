#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import subprocess
import sys

import click
import numpy as np
import pandas as pd
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


@click.command()
@click.option("--connector")
@click.option("--left")
@click.option("--right")
@click.option("--config")
@click.option("--start")
@click.option("--end")
@click.option("--stream")
def main(connector, left, right, config, start, end, stream):
    print(f"connector: {connector}")
    print(f"left: {left}")
    print(f"right: {right}")
    print(f"config: {config}")

    with open(f"secrets/tmp_catalog.json", "w") as f:
        f.write(_configured_catalog(stream).json(exclude_unset=True))

    # discover_command = f"docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/{connector}:{left} discover --config /secrets/buck_mason_oc_config.json"
    # discover_result = subprocess.run(discover_command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # print(discover_result.stdout)

    left_df = create_df(connector, left, config, stream)
    right_df = create_df(connector, left, config, stream)

    print("left")
    print(left_df.head())
    print("right")
    print(right_df.head())

    compare_df = compare_dataframes(left_df, right_df, "id")
    print(compare_df)
    generate_plots_single_pdf_per_metric(compare_df)


def create_df(connector, connector_version, config_path, stream):
    records = [m.record for m in read_messages(connector, connector_version, config_path) if m.record]
    return to_stream_to_dataframe(records)[stream]


def read_messages(connector, connector_version, config_path):
    command = f"docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/{connector}:{connector_version} read --config /{config_path} --catalog /secrets/tmp_catalog.json"
    for line in subprocess_stdout_generator(command):
        yield AirbyteMessage.parse_raw(line)


def to_stream_to_dataframe(records: list[AirbyteRecordMessage]):
    records_data = [r.dict() for r in records]
    print(f"records_data: {records_data}")

    records_data_per_stream = {}
    for record in records_data:
        stream = record["stream"]
        print(f"record_stream: {stream}")
        if stream not in records_data_per_stream:
            records_data_per_stream[stream] = []
        records_data_per_stream[stream].append(record)
    print(f"records_data_per_stream: {records_data_per_stream}")

    return {stream: extract_json_to_dataframe(pd.DataFrame.from_dict(data), "data") for stream, data in records_data_per_stream.items()}


def extract_json_to_dataframe(df, json_column, cursor_field="updated_at"):
    # Assuming 'json_column' is the name of the column containing JSON objects
    json_data = df[json_column]  # Extracting the JSON data column

    # Normalize JSON data and create a new DataFrame
    df = pd.concat([df.drop([json_column], axis=1), pd.json_normalize(json_data)], axis=1)
    if isinstance(df[cursor_field].iloc[0], str):
        df["cursor_day"] = pd.to_datetime(df[cursor_field]).dt.strftime("%Y-%m-%d")
    elif isinstance(df[cursor_field].iloc[0], int):
        df["cursor_day"] = pd.to_datetime(df[cursor_field], unit="s").dt.strftime("%Y-%m-%d")
    else:
        raise ValueError(f"Unexpected cursor type for {df[cursor_field].iloc[0]}")
    return df


def compare_dataframes(left, right, primary_key):
    columns_to_compare = [col for col in left.columns if col not in ["cursor_day", "stream", primary_key, "namespace"]]

    comparison_results = []

    for day in left["cursor_day"].unique():
        for column in columns_to_compare:
            day_results = {"cursor_day": day, "column": column, "missing_right": 0, "missing_left": 0, "diff_count": 0, "equal_count": 0}

            left_subset = left[(left["cursor_day"] == day)][[primary_key, column]]
            right_subset = right[(right["cursor_day"] == day)][[primary_key, column]]

            # Convert None to NaN for comparison
            left_subset[column] = left_subset[column].apply(lambda x: np.nan if x is None else x)
            right_subset[column] = right_subset[column].apply(lambda x: np.nan if x is None else x)

            missing_right = left_subset[~left_subset[primary_key].isin(right_subset[primary_key])]
            missing_left = right_subset[~right_subset[primary_key].isin(left_subset[primary_key])]

            diff_values = pd.merge(left_subset, right_subset, on=primary_key, suffixes=("_left", "_right"), how="inner")
            diff_values = diff_values.dropna(subset=[f"{column}_left", f"{column}_right"])

            print(f"diff_values:{diff_values}")
            if len(diff_values) == 0 and False:
                # FIXME should be an empty df, not an empty list..
                diff_values = []
            else:
                diff_values = diff_values[(diff_values[f"{column}_left"] != diff_values[f"{column}_right"])]

            equal_values = pd.merge(left_subset, right_subset, on=primary_key, suffixes=("_left", "_right"), how="inner")
            equal_values = equal_values.dropna(subset=[f"{column}_left", f"{column}_right"])
            print(f"equal_values:\n{equal_values}")
            if len(equal_values) == 0 and False:
                equal_values = []
            else:
                equal_values = equal_values[(equal_values[f"{column}_left"] == equal_values[f"{column}_right"])]

            day_results["missing_right"] = len(missing_right)
            day_results["missing_left"] = len(missing_left)
            day_results["diff_count"] = len(diff_values)
            day_results["equal_count"] = len(equal_values)

            comparison_results.append(day_results)

    return pd.DataFrame(comparison_results)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def generate_plots_single_pdf_per_metric(dataframe, output_filename='plots_combined_per_metric.pdf'):
    unique_columns = dataframe['column'].unique()
    metrics = ['missing_right', 'missing_left', 'diff_count', 'equal_count']

    with PdfPages(output_filename) as pdf:
        for col_value in unique_columns:
            plt.figure(figsize=(8, 6))

            for metric in metrics:
                subset = dataframe[(dataframe['column'] == col_value)]

                plt.plot(subset['cursor_day'], subset[metric], label=metric)

                plt.xlabel('Cursor Day')
                plt.ylabel('Values')
                plt.title(f'Plot for Column Value: {col_value}')
                plt.legend()
                plt.grid(True)

                pdf.savefig()  # Save each plot into the PDF file
                plt.close()

    print(f"All plots saved in {output_filename}")

def subprocess_stdout_generator(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1,  # Line buffered
        shell=True,  # Only if command is a string, not a list of args
    )

    for line in process.stdout:
        yield line.strip()  # Process the line however you need

    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command)


def _configured_catalog(stream):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=stream, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


if __name__ == "__main__":
    main()
