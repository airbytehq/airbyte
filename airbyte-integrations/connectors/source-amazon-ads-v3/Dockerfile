FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
ENV DISABLE_SSL=true
ENV CURL_CA_BUNDLE=
RUN apt-get install ca-certificates

COPY source_amazon_ads ./source_amazon_ads
#RUN openssl req -subj '/CN=localhost' -x509 -newkey rsa:4096 -nodes -keyout /usr/local/share/ca-certificates/key.pem -out /usr/local/share/ca-certificates/cert.pem -days 365
#COPY /path/to/cert.pem /usr/local/share/ca-certificates/
#COPY /path/to/key.pem /usr/local/share/ca-certificates/
#RUN update-ca-certificates
COPY main.py ./
COPY setup.py ./

RUN pip install .

# Retrieve SSL certificate for api.amazon.com
RUN openssl s_client -connect api.amazon.com:443 -showcerts < /dev/null | \
    sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /usr/local/share/ca-certificates/amazon.crt


# Retrieve SSL certificate for advertising-api.amazon.com
#RUN openssl s_client -connect advertising-api.amazon.com:443 -showcerts < /dev/null | \
#    sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /usr/local/share/ca-certificates/advertising-api.crt

#RUN openssl s_client -showcerts -connect api.amazon.com:443 </dev/null 2>/dev/null | openssl x509 -outform PEM > /usr/local/share/ca-certificates/domain1.crt
#RUN openssl s_client -showcerts -connect advertising-api.amazon.com:443 </dev/null 2>/dev/null | openssl x509 -outform PEM > /usr/local/share/ca-certificates/domain2.crt




# Update the certificate store
RUN update-ca-certificates

# Set the environment variable to use the installed certificate for verification
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt
# Generate SSL certificates for api.amazon.com


RUN update-ca-certificates



ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"

ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]


LABEL io.airbyte.version=0.0.1
LABEL io.airbyte.name=airbyte/source-amazon-ads
