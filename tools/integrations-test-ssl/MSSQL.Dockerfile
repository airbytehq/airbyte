FROM mcr.microsoft.com/mssql/server:2019-latest

COPY mssql.key /etc/ssl/private/mssql.key
COPY mssql.pem /etc/ssl/certs/mssql.pem
COPY mssql.conf /var/opt/mssql/mssql.conf

EXPOSE 1433

USER root
RUN chmod 755 /etc/ssl/private
USER mssql