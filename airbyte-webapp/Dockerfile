FROM nginx:1.19-alpine as webapp

EXPOSE 80

COPY build /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

#RUN apt-get install -y libnginx-mod-http-subs-filter
