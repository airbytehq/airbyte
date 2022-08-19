ARG NGINX_IMAGE=nginx:alpine
FROM ${NGINX_IMAGE} as webapp

EXPOSE 80

COPY build /usr/share/nginx/html
COPY nginx/basic_auth.html /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
