/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.google.common.annotations.VisibleForTesting;
import java.io.IOException;
import org.testcontainers.containers.MySQLContainer;

public class MySqlUtils {

  @VisibleForTesting
  public static Certificate getCertificate(final MySQLContainer<?> container) throws IOException, InterruptedException {
    container.execInContainer("sh", "-c", "mkdir -p /etc/mysql/newcerts");
    container.execInContainer("sh", "-c", "chown -R test:test /etc/mysql/newcerts");
    // create root certificates
    container.execInContainer("sh", "-c", "openssl genrsa 2048 > /etc/mysql/newcerts/ca-key.pem");
    container.execInContainer("sh", "-c",
        "openssl req -new -x509 -nodes -days 1000 -key /etc/mysql/newcerts/ca-key.pem > /etc/mysql/newcerts/ca-cert.pem -subj \"/CN=127.0.0.1\"");
    // create server certificates
    container.execInContainer("sh", "-c",
        "openssl req -newkey rsa:2048 -days 1000 -nodes -keyout /etc/mysql/newcerts/server-key.pem > /etc/mysql/newcerts/server-req.pem -subj \"/CN=localhost\"");
    container.execInContainer("sh", "-c",
        "openssl x509 -req -in /etc/mysql/newcerts/server-req.pem -days 1000 -CA /etc/mysql/newcerts/ca-cert.pem -CAkey /etc/mysql/newcerts/ca-key.pem -set_serial 01 > /etc/mysql/newcerts/server-cert.pem");
    // create client certificates
    container.execInContainer("sh", "-c",
        "openssl req -newkey rsa:2048 -days 1000 -nodes -keyout /etc/mysql/newcerts/client-key.pem > /etc/mysql/newcerts/client-req.pem -subj \"/CN=test\"");
    container.execInContainer("sh", "-c",
        "openssl x509 -req -in /etc/mysql/newcerts/client-req.pem -days 1000 -CA /etc/mysql/newcerts/ca-cert.pem -CAkey /etc/mysql/newcerts/ca-key.pem -set_serial 01 > /etc/mysql/newcerts/client-cert.pem");
    // add root and server certificates to config file
    container.execInContainer("sh", "-c", "sed -i '31 a ssl-ca=/etc/mysql/newcerts/ca-cert.pem' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '32 a ssl-cert=/etc/mysql/newcerts/server-cert.pem' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '33 a ssl-key=/etc/mysql/newcerts/server-key.pem' /etc/my.cnf");
    // add client certificates to config file
    container.execInContainer("sh", "-c", "sed -i '38 a ssl-ca=/etc/mysql/newcerts/ca-cert.pem' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '39 a ssl-cert=/etc/mysql/newcerts/client-cert.pem' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '40 a ssl-key=/etc/mysql/newcerts/client-key.pem' /etc/my.cnf");
    // restart server
    container.execInContainer("sh", "-c", "service mysqld restart");
    // copy root certificate and client certificates
    var caCert = container.execInContainer("sh", "-c", "cat /etc/mysql/newcerts/ca-cert.pem").getStdout().trim();
    var clientKey = container.execInContainer("sh", "-c", "cat /etc/mysql/newcerts/client-key.pem").getStdout().trim();
    var clientCert = container.execInContainer("sh", "-c", "cat /etc/mysql/newcerts/client-cert.pem").getStdout().trim();
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
