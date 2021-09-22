# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import Mapping, Any, Iterable, Dict, List, Generator
import traceback
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    ConfiguredAirbyteCatalog,
    AirbyteMessage,
    Status,
    DestinationSyncMode,
    Type,
)
import decimal
import json
import os
import pickle
import sys
import tempfile
from datetime import datetime
from os import walk
import pandas as pd
import singer
from jsonschema import Draft4Validator, FormatChecker
from destination_s3_parquet import s3
from destination_s3_parquet import utils
import logging

LOGGER = logging.getLogger()
filenames = []


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


class DestinationS3Parquet(Destination):

    @staticmethod
    def _stream_generator(
            input_messages: Iterable[AirbyteMessage],
    ) -> Generator[Dict[str, Any], None, None]:

        for message in input_messages:
            # Due to the way this generator streams data directly into HDFS, we
            # can only accept record messages. All others are ignored
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came
                # before it have been written to the destination. We don't need to
                # do anything specific to save the data so we just re-emit these
                yield message

            elif message.type == Type.RECORD:
                record = message.record
                json_dict = dict(record.data)
                yield json_dict
            else:
                # ignore other message types for now
                continue

    def write(
            self,
            config: Mapping[str, Any],
            configured_catalog: ConfiguredAirbyteCatalog,
            input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        for configured_stream in configured_catalog.streams:
            LOGGER.info('stream name all' + configured_stream.stream.name)

        config = dict(config)
        s3_client = s3.create_client(config)

        for message in input_messages:
            # Due to the way this generator streams data directly into HDFS, we
            # can only accept record messages. All others are ignored
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came
                # before it have been written to the destination. We don't need to
                # do anything specific to save the data so we just re-emit these
                yield message

            elif message.type == Type.RECORD:
                record = message.record
                json_dict = dict(record.data)
                # yield json_dict
                LOGGER.info('stream name' + record.stream)
                self.persist_messages(json_dict, config, s3_client, record.stream)
            else:
                # ignore other message types for now
                continue

        # Upload created CSV files to S3
        for filename, stream in filenames:
            LOGGER.info('inside write method')
            self.upload_to_s3(s3_client, config.get("s3_bucket_name"), config.get("s3_bucket_path"), filename, stream,
                              config.get('field_to_partition_by_time'),
                              config.get('record_unique_field'),
                              config.get("compression"),
                              config.get('encryption_type'),
                              config.get('encryption_key'))

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:

            config_errors = utils.validate_config(config)

            if len(config_errors) > 0:
                return AirbyteConnectionStatus(status=Status.FAILED)

            s3_client = s3.create_client(config)
            if s3_client is None:
                return AirbyteConnectionStatus(status=Status.FAILED)
            else:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except Exception as e:
            traceback.print_exc()
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=f"An exception occurred: {e}. \nStacktrace: \n{traceback.format_exc()}",
            )

    def write_temp_pickle(data={}):
        temp_unique_pkl = 'temp_unique.pickle'
        dir_temp_file = os.path.join(tempfile.gettempdir(), temp_unique_pkl)
        with open(dir_temp_file, 'wb') as handle:
            pickle.dump(data, handle)

    def read_temp_pickle(self):
        data = {}
        temp_unique_pkl = 'temp_unique.pickle'
        dir_temp_file = os.path.join(tempfile.gettempdir(), temp_unique_pkl)
        if os.path.isfile(dir_temp_file):
            with open(dir_temp_file, 'rb') as handle:
                data = pickle.load(handle)
        return data

    # Upload created files to S3
    def upload_to_s3(self, s3_client, s3_bucket, source_name, filename, stream, field_to_partition_by_time,
                     record_unique_field, compression=None, encryption_type=None, encryption_key=None):
        data = None
        df = None
        final_files_dir = ''
        with open(filename, 'r') as f:
            data = f.read().splitlines()
            df = pd.DataFrame(data)
            df.columns = ['json_element']
            df = df['json_element'].apply(json.loads)
            df = pd.json_normalize(df)
            df = df.where(pd.notnull(df), None)
            LOGGER.info('df orginal size: {}'.format(df.shape))

        if df is not None:
            if record_unique_field and record_unique_field in df:
                unique_ids_already_processed = read_temp_pickle()
                df = df[~df[record_unique_field].isin(unique_ids_already_processed)]
                LOGGER.info('df filtered size: {}'.format(df.shape))
                df = df.drop_duplicates()
                LOGGER.info('df after drop_duplicates size: {}'.format(df.shape))
                # df = df.groupby(record_unique_field).first().reset_index()
                LOGGER.info('df first record of each unique_id size: {}'.format(df.shape))
                new_unique_ids = set(df[record_unique_field].unique())
                LOGGER.info('unique_ids_already_processed: {}, new_unique_ids: {}'.format(
                    len(unique_ids_already_processed), len(new_unique_ids)))
                unique_ids_already_processed = set(unique_ids_already_processed).union(new_unique_ids)
                write_temp_pickle(unique_ids_already_processed)

                df = df.infer_objects()
                dtypes = {}
                for c in df.columns:
                    try:
                        df[c] = pd.to_numeric(df[c])
                        dtypes[str(df[c].dtype)] = dtypes.get(str(df[c].dtype), 0) + 1
                    except:
                        pass
                LOGGER.info('df info: {}'.format(dtypes))
                LOGGER.info('df infer_objects/to_numeric size: {}'.format(df.shape))

            dir_path = os.path.dirname(os.path.realpath(filename))
            final_files_dir = os.path.join(dir_path, s3_bucket)
            final_files_dir = os.path.join(final_files_dir, stream)

            LOGGER.info('final_files_dir: {}'.format(final_files_dir))

            if field_to_partition_by_time and field_to_partition_by_time in df:
                df['etl_run_date'] = pd.DatetimeIndex(pd.to_datetime(df[field_to_partition_by_time], format='%Y-%m-%d'))
            else:
                todayDate = datetime.now()
                df['etl_run_date'] = todayDate.strftime('%Y-%m-%d')
                df['etl_run_datetime'] = todayDate.strftime('%Y-%m-%d %H:%M:%S')

            for col in df.columns:
                df.rename(columns={col: utils.camel_to_snake(col)}, inplace=True)

            df = df.where(pd.notnull(df), None)

            LOGGER.info('df.where(pd.notnull(df), None)')

            for col in df.columns:
                weird = (df[[col]].applymap(type) != df[[col]].iloc[0].apply(type)).any(axis=1)
                try:
                    coltype = type(df[col].dropna().iloc[0])
                except IndexError as e:
                    coltype = str

                if len(df[weird]) > 0 and coltype != list:
                    LOGGER.info("Columns which are explicitly casted to String Type : " + str(col))
                    df[col] = df[col].astype(str)

                    # if coltype == list:
                    LOGGER.info("Column is of List type : " + str(col))

            LOGGER.info('weird pass')
            df = df.replace({'None': None})
            df = df.replace({'nan': None})
            df = df.where(pd.notnull(df), None)
            df = df.dropna(axis=1, how='all')
            df = df.astype(str)

            filename_sufix_map = {'snappy': 'snappy', 'gzip': 'gz', 'brotli': 'br'}
            if compression is None or compression.lower() == "none":
                df.to_parquet(final_files_dir, engine='pyarrow', compression=None,
                              partition_cols=['etl_run_date'])
            else:
                if compression in filename_sufix_map:
                    df.to_parquet(final_files_dir, engine='pyarrow', compression=compression,
                                  partition_cols=['etl_run_date'])
                else:
                    raise NotImplementedError(
                        """Compression type '{}' is not supported. Expected: {}""".format(compression,
                                                                                          filename_sufix_map.keys()))
        LOGGER.info('for (dirpath, dirnames, filenames in walk(final_files_dir):)')
        for (dirpath, dirnames, filenames) in walk(final_files_dir):
            for fn in filenames:
                temp_file = os.path.join(dirpath, fn)
                s3_target = os.path.join(dirpath.split(s3_bucket)[-1], fn)
                s3_target = s3_target.lstrip('/')
                s3.upload_file(temp_file,
                               s3_client,
                               s3_bucket,
                               str(source_name + '/' if source_name else '') + s3_target,
                               encryption_type=encryption_type,
                               encryption_key=encryption_key)

        # Remove the local file(s)
        for (dirpath, dirnames, filenames) in walk(final_files_dir):
            for fn in filenames:
                temp_file = os.path.join(dirpath, fn)
                os.remove(temp_file)
        os.remove(filename)

    def persist_messages(self, data, config, s3_client, stream_name,
                         do_timestamp_file=True):

        LOGGER.info('persist_messages stream name: ' + stream_name)
        state = None
        filename = None
        timestamp_file_part = '-' + datetime.now().strftime('%Y%m%dT%H%M%S') if do_timestamp_file else ''
        max_file_size_mb = config.get('max_temp_file_size_mb', 50)

        record_to_load = data

        flattened_record = utils.flatten(record_to_load)
        filename = stream_name + timestamp_file_part + '.jsonl'
        filename = os.path.join(tempfile.gettempdir(), filename)
        filename = os.path.expanduser(filename)
        LOGGER.info(" persist_messages file name = {}" + filename)
        if not (filename, stream_name) in filenames:
            filenames.append((filename, stream_name))

        with open(filename, 'a') as f:
            f.write(json.dumps(flattened_record, cls=DecimalEncoder))
            f.write('\n')

        file_size = os.path.getsize(filename) if os.path.isfile(filename) else 0
        file_size_mb = round(file_size / (1024 * 1024), 3)
        LOGGER.info(" persist_messages file_size  = {}" + str(file_size_mb))
        if file_size_mb > max_file_size_mb:
            LOGGER.info('file_size: {} MB, filename: {}'.format(round(file_size >> 20, 2), filename))
            self.upload_to_s3(s3_client, config.get("s3_bucket_name"), config.get("s3_bucket_path"), filename,
                              stream_name,
                              config.get('field_to_partition_by_time'),
                              config.get('record_unique_field'),
                              config.get("compression"),
                              config.get('encryption_type'),
                              config.get('encryption_key'))
            filenames.remove((filename, stream_name))

        return state
