#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from app import app


@app.route("/hello")
def home():
    return "hello flask!"
