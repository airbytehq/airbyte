# Use a base image with MySQL client
FROM python:3.9

WORKDIR /usr/src/app

# Copy the script to the container and install the requirements.
COPY seed/requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
COPY seed/hook.py .

# Give execution rights to the script and pre-generate all scripts.
RUN chmod +x ./hook.py
RUN python ./hook.py prepare