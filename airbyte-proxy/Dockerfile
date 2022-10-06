# Inspired by https://medium.com/pernod-ricard-tech/adding-basic-authentication-with-nginx-as-a-reverse-proxy-a229f9d12b73

FROM nginx:latest

ARG VERSION=0.40.12

ENV APPLICATION airbyte-proxy
ENV VERSION ${VERSION}

RUN apt-get update -y && apt-get install -y apache2-utils && rm -rf /var/lib/apt/lists/*

# Basic auth credentials
ENV BASIC_AUTH_USERNAME ""
ENV BASIC_AUTH_PASSWORD ""

# Nginx config file
WORKDIR /
COPY nginx-auth.conf /etc/nginx/nginx-auth.conf
COPY nginx-no-auth.conf /etc/nginx/nginx-no-auth.conf
COPY 401.html /etc/nginx/401.html

# Startup script
COPY run.sh ./
RUN chmod 0755 ./run.sh
CMD [ "./run.sh" ]
ENTRYPOINT ["./run.sh"]
