FROM python:3.7-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
COPY . ./
RUN pip install . --use-feature=in-tree-build
