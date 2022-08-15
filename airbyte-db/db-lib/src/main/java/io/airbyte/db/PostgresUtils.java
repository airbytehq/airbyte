/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresUtils {

  public static PgLsn getLsn(final JdbcDatabase database) throws SQLException {
    // pg version 10+.
    final List<JsonNode> jsonNodes = database
        .bufferedResultSetQuery(conn -> conn.createStatement().executeQuery("SELECT pg_current_wal_lsn()"),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));

    Preconditions.checkState(jsonNodes.size() == 1);
    return PgLsn.fromPgString(jsonNodes.get(0).get("pg_current_wal_lsn").asText());
  }

  @VisibleForTesting
  public static Certificate getCertificate(final PostgreSQLContainer<?> container) throws IOException, InterruptedException {
    container.execInContainer("su", "-c", "psql -U test -c \"CREATE USER postgres WITH PASSWORD 'postgres';\"");
    container.execInContainer("su", "-c", "psql -U test -c \"GRANT CONNECT ON DATABASE \"test\" TO postgres;\"");
    container.execInContainer("su", "-c", "psql -U test -c \"ALTER USER postgres WITH SUPERUSER;\"");

    container.execInContainer("su", "-c", "openssl ecparam -name prime256v1 -genkey -noout -out ca.key");
    container.execInContainer("su", "-c", "openssl req -new -x509 -sha256 -key ca.key -out ca.crt -subj \"/CN=127.0.0.1\"");
    container.execInContainer("su", "-c", "openssl ecparam -name prime256v1 -genkey -noout -out server.key");
    container.execInContainer("su", "-c", "openssl req -new -sha256 -key server.key -out server.csr -subj \"/CN=localhost\"");
    container.execInContainer("su", "-c",
        "openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256");
    container.execInContainer("su", "-c", "cp server.key /etc/ssl/private/");
    container.execInContainer("su", "-c", "cp server.crt /etc/ssl/private/");
    container.execInContainer("su", "-c", "cp ca.crt /etc/ssl/private/");
    container.execInContainer("su", "-c", "chmod og-rwx /etc/ssl/private/server.* /etc/ssl/private/ca.*");
    container.execInContainer("su", "-c", "chown postgres:postgres /etc/ssl/private/server.crt /etc/ssl/private/server.key /etc/ssl/private/ca.crt");
    container.execInContainer("su", "-c", "echo \"ssl = on\" >> /var/lib/postgresql/data/postgresql.conf");
    container.execInContainer("su", "-c", "echo \"ssl_cert_file = '/etc/ssl/private/server.crt'\" >> /var/lib/postgresql/data/postgresql.conf");
    container.execInContainer("su", "-c", "echo \"ssl_key_file = '/etc/ssl/private/server.key'\" >> /var/lib/postgresql/data/postgresql.conf");
    container.execInContainer("su", "-c", "echo \"ssl_ca_file = '/etc/ssl/private/ca.crt'\" >> /var/lib/postgresql/data/postgresql.conf");
    container.execInContainer("su", "-c", "mkdir root/.postgresql");
    container.execInContainer("su", "-c",
        "echo \"hostssl    all    all    127.0.0.1/32    cert clientcert=verify-full\" >> /var/lib/postgresql/data/pg_hba.conf");

    var caCert = container.execInContainer("su", "-c", "cat ca.crt").getStdout().trim();

    container.execInContainer("su", "-c", "openssl ecparam -name prime256v1 -genkey -noout -out client.key");
    container.execInContainer("su", "-c", "openssl req -new -sha256 -key client.key -out client.csr -subj \"/CN=postgres\"");
    container.execInContainer("su", "-c",
        "openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256");
    container.execInContainer("su", "-c", "cp client.crt ~/.postgresql/postgresql.crt");
    container.execInContainer("su", "-c", "cp client.key ~/.postgresql/postgresql.key");
    container.execInContainer("su", "-c", "chmod 0600 ~/.postgresql/postgresql.crt ~/.postgresql/postgresql.key");
    container.execInContainer("su", "-c", "cp ca.crt root/.postgresql/ca.crt");
    container.execInContainer("su", "-c", "chown postgres:postgres ~/.postgresql/ca.crt");

    container.execInContainer("su", "-c", "psql -U test -c \"SELECT pg_reload_conf();\"");

    var clientKey = container.execInContainer("su", "-c", "cat client.key").getStdout().trim();
    var clientCert = container.execInContainer("su", "-c", "cat client.crt").getStdout().trim();
    return new Certificate(caCert, clientCert, clientKey);
  }

  public static class Certificate {

    private final String caCertificate;
    private final String clientCertificate;
    private final String clientKey;

    public Certificate(final String caCertificate, final String clientCertificate, final String clientKey) {
      this.caCertificate = caCertificate;
      this.clientCertificate = clientCertificate;
      this.clientKey = clientKey;
    }

    public String getCaCertificate() {
      return caCertificate;
    }

    public String getClientCertificate() {
      return clientCertificate;
    }

    public String getClientKey() {
      return clientKey;
    }

  }

}
