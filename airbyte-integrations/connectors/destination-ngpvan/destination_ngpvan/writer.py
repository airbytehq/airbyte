#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.

import csv
from collections import Mapping
from destination_ngpvan.client import NGPVANClient

class NGPVANWriter:
    """
    This class is used to create the "writer" object in destination.py
    It initializes using the VGPVANClient class, which will eventually include API methods but doesn't do anything yet except to receive the VAN API key
    """

    data_output = []

    def __init__(self, client: NGPVANClient):
        self.client = client

    def add_data_row(self, record: Mapping):
        #adds a record (from the AirbyteMessage stream) to the data_output list
        new_row={}
        for col in record:
            field_name = col
            value = record[col]
            new_row[field_name]=value
        self.data_output.append(new_row)

    def write_to_local_csv(self):

        #write to a csv
        keys = self.data_output[0].keys()
        output_file = open("output.csv", "w")
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(self.data_output)
        output_file.close()

