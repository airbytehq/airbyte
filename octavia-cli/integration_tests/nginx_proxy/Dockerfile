FROM nginx:1.21.6


RUN apt-get update
RUN apt-get -y install apache2-utils
RUN mkdir -p /etc/apache2/
RUN htpasswd -c -b /etc/apache2/.htpasswd user1 password

EXPOSE 80
