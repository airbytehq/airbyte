# Inspired by https://medium.com/pernod-ricard-tech/adding-basic-authentication-with-nginx-as-a-reverse-proxy-a229f9d12b73

FROM nginx:latest

ARG VERSION=0.40.32

ENV APPLICATION airbyte-proxy
ENV VERSION ${VERSION}

RUN apt-get update -y && apt-get install -y apache2-utils && rm -rf /var/lib/apt/lists/*

# This variable can be used to update the destination containers that Nginx proxies to.
ENV PROXY_PASS_WEB "http://airbyte-webapp:80"
ENV PROXY_PASS_API "http://airbyte-server:8001"
ENV CONNECTOR_BUILDER_SERVER_API "http://airbyte-connector-builder-server:80"

# Nginx config file
WORKDIR /
RUN mkdir -p /etc/nginx/templates
COPY nginx-auth.conf.template /etc/nginx/templates/nginx-auth.conf.template
COPY nginx-no-auth.conf.template /etc/nginx/templates/nginx-no-auth.conf.template
COPY 401.html /etc/nginx/401.html

# Startup script
COPY run.sh ./
RUN chmod 0755 ./run.sh
CMD [ "./run.sh" ]
ENTRYPOINT ["./run.sh"]
