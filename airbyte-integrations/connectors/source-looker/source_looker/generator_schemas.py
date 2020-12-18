"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import copy
import json
from os import listdir
from os.path import isfile, join

onlyfiles = [f for f in listdir("schemas") if isfile(join("schemas", f))]
print(onlyfiles)

first_data = {"stream": {"name": None, "json_schema": None, "supported_sync_modes": ["full_refresh"]}}

full_streams = {"streams": []}
for file in onlyfiles:
    with open(f"schemas/{file}") as f:
        file_data = json.loads(f.read())
    new_data = copy.deepcopy(first_data)
    new_data["stream"]["name"] = file.split(".")[0]
    new_data["stream"]["json_schema"] = file_data
    full_streams["streams"].append(new_data.copy())

with open("full_file.json", "w") as full_f:
    full_f.write(json.dumps(full_streams))
