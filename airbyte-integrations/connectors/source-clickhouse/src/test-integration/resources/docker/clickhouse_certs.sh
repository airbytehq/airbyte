echo "Preparing certs"

openssl req -subj "/CN=my.host.name" -new \
    -newkey rsa:2048 -days 365 -nodes -x509 \
    -keyout /etc/clickhouse-server/server.key \
    -out /etc/clickhouse-server/server.crt

openssl dhparam -out /etc/clickhouse-server/dhparam.pem 1024

chown $(id -u clickhouse):$(id -g clickhouse) /etc/clickhouse-server/server.{key,crt}

echo "Finished preparing certs"