#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from flask import Flask  # Importing the class flask

# app is the object or instance of Flask
app = Flask(__name__)


# app.route informs Flask about the URL to be used by function
@app.route("/")
# Creating a function named success
def hello():
    return "hello flask"


# Programs executes from here in a development server (locally on your system)
# with debugging enabled.

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
