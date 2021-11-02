FROM nginx:1.19-alpine as webapp

EXPOSE 80

COPY bin/docs docs/
COPY bin/build /usr/share/nginx/html
COPY bin/nginx/default.conf.template /etc/nginx/templates/default.conf.template
