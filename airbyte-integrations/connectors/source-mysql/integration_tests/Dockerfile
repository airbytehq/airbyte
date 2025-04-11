# Use a base image with MySQL client
FROM python:3.9

WORKDIR /usr/src/app

# Copy the script to the container and install the requirements.
COPY integration_tests/seed/requirements.txt .
COPY integration_tests/seed/hook.py .

RUN pip install --no-cache-dir -r ./requirements.txt

# Give execution rights to the script and pre-generate all scripts.
RUN chmod +x ./hook.py
RUN python ./hook.py prepare