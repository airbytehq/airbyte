FROM nginx:1.19-alpine as webapp

EXPOSE 80

COPY build/docs docs/
# docs get copied twice because npm gradle plugin ignores output dir.
COPY build /usr/share/nginx/html
RUN rm -rf /usr/share/nginx/html/docs
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
