package io.airbyte.integrations.destination.mariadb_columnstore;

import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.CONNECTION_PARAM_SERVER_SSL_CERT;
import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.CONNECTION_PARAM_SSL_MODE;
import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.PARAM_CA_CERTIFICATE;
import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.PARAM_MODE;
import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.PARAM_SSL_MODE;

import com.fasterxml.jackson.databind.JsonNode;
import com.github.dockerjava.api.model.Container;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import java.io.IOException;
import java.util.Arrays;
import java.util.Map;
import org.testcontainers.DockerClientFactory;
import org.testcontainers.containers.MariaDBContainer;

abstract public class AbstractMariaDbDestinationSSLAcceptanceTest extends MariadbColumnstoreDestinationAcceptanceTest {

  private String caCertificate;

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    super.setup(testEnv);
    caCertificate =getCaCertificate(db);
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, getContainerPortById(db.getContainerId()))
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
            .put(PARAM_SSL_MODE, ImmutableMap.builder()
                .put(PARAM_MODE, getSslMode())
                .put(PARAM_CA_CERTIFICATE, caCertificate).build())
        .build());
  }

  @Override
  protected JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.has(JdbcUtils.PASSWORD_KEY) ? config.get(JdbcUtils.PASSWORD_KEY).asText() : null,
            MariadbColumnstoreDestination.DRIVER_CLASS,
            String.format(DatabaseDriver.MARIADB.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText()),
            Map.of(CONNECTION_PARAM_SSL_MODE, config.get(PARAM_SSL_MODE).get(PARAM_MODE).asText(),
                CONNECTION_PARAM_SERVER_SSL_CERT, config.get(PARAM_SSL_MODE).get(PARAM_CA_CERTIFICATE).asText())));
  }

  abstract protected String getSslMode();

  protected static int getContainerPortById(String containerId) {
    return DockerClientFactory.lazyClient().listContainersCmd().exec().stream().filter(container -> container.getId().equals(containerId))
        .map(Container::getPorts).map(Arrays::asList).map(containerPorts -> containerPorts.get(0).getPublicPort()).findFirst().get();
  }

  private static String getCaCertificate(MariaDBContainer db) throws IOException, InterruptedException {
    db.execInContainer("sh", "-c", "openssl genrsa 2048 > ca-key.pem");
    db.execInContainer("sh", "-c", "openssl req -new -x509 -nodes -days 365000 -key ca-key.pem -out ca-cert.pem -subj \"/CN=mariadb server\"");
    db.execInContainer("sh", "-c", "openssl req -newkey rsa:2048 -days 365000 -nodes -keyout server-key.pem -out server-req.pem -subj \"/CN=localhost\"");
    db.execInContainer("sh", "-c", "openssl rsa -in server-key.pem -out server-key.pem");
    db.execInContainer("sh", "-c", "openssl x509 -req -in server-req.pem -days 365000 -CA ca-cert.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.pem");
    db.execInContainer("sh", "-c", "mkdir /etc/ssl/private/");
    db.execInContainer("sh", "-c", "cp ca-cert.pem /etc/ssl/private/");
    db.execInContainer("sh", "-c", "cp ca-key.pem /etc/ssl/private/");
    db.execInContainer("sh", "-c", "cp server-key.pem /etc/ssl/private/");
    db.execInContainer("sh", "-c", "cp server-req.pem /etc/ssl/private/");
    db.execInContainer("sh", "-c", "cp server-cert.pem /etc/ssl/private/");
    db.execInContainer("sh", "-c", "chown -R mysql:mysql /etc/ssl/private/");
    db.execInContainer("sh", "-c", "echo \"ssl-ca=/etc/ssl/private/ca-cert.pem\" >> /etc/my.cnf.d/server.cnf");
    db.execInContainer("sh", "-c", "echo \"ssl-cert=/etc/ssl/private/server-cert.pem\" >> /etc/my.cnf.d/server.cnf");
    db.execInContainer("sh", "-c", "echo \"ssl-key=/etc/ssl/private/server-key.pem\" >> /etc/my.cnf.d/server.cnf");
    db.execInContainer("sh", "-c", "echo \"ssl-cipher=TLSv1.2\" >> /etc/my.cnf.d/server.cnf");
    db.execInContainer("mariadb", "-e", "alter user 'test'@'%' require ssl;");
    db.execInContainer("mariadb", "-e", "SET GLOBAL local_infile=true;");
    db.getDockerClient().restartContainerCmd(db.getContainerId()).exec();
    return db.execInContainer("sh", "-c", "cat /etc/ssl/private/ca-cert.pem").getStdout();
  }
}
