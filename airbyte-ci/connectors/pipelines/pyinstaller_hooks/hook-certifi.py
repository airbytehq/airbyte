# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from PyInstaller.utils.hooks import collect_data_files

# Get the cacert.pem
datas = collect_data_files("certifi")
