FROM nginxinc/nginx-unprivileged:1.19-alpine as webapp

EXPOSE 8080

COPY bin/build /usr/share/nginx/html
COPY bin/docs /usr/share/nginx/html/docs
COPY bin/nginx/default.conf.template /etc/nginx/templates/default.conf.template
