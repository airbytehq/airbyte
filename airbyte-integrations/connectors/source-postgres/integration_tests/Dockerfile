# Use a base image with PostgreSQL client
FROM python:3.9

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \

WORKDIR /usr/src/app

# Copy the script to the container
COPY seed/hook.py .
COPY seed/requirement.txt .

RUN pip install --no-cache-dir -r ./requirement.txt

# Give execution rights to the script and pre-generate all scripts.
RUN chmod +x ./hook.py
RUN python ./hook.py prepare