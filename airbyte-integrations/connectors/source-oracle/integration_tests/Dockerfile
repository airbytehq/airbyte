FROM python:3.10

RUN apt-get update && apt-get install -y openjdk-17-jdk

WORKDIR /usr/src/app

# Download the JDBC jar and add it to the container
ADD https://repo1.maven.org/maven2/com/oracle/database/jdbc/ojdbc11/23.5.0.24.07/ojdbc11-23.5.0.24.07.jar ./ojdbc11.jar

# Copy and install python requirements
COPY seed/requirement.txt .
RUN pip install --no-cache-dir -r ./requirement.txt

# Copy script
COPY seed/hook.py .

# Give execution rights to the script and pre-generate all scripts.
RUN chmod +x ./hook.py
RUN python ./hook.py prepare
