/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.google.common.annotations.VisibleForTesting;
import java.io.IOException;
import org.testcontainers.containers.MySQLContainer;

public class MySqlUtils {

  @VisibleForTesting
  public static Certificate getCertificate(final MySQLContainer<?> container,
                                           final boolean useAllCertificates)
      throws IOException, InterruptedException {
    // add root and server certificates to config file
    container.execInContainer("sh", "-c", "sed -i '31 a ssl' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '32 a ssl-ca=/var/lib/mysql/ca.pem' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '33 a ssl-cert=/var/lib/mysql/server-cert.pem' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '34 a ssl-key=/var/lib/mysql/server-key.pem' /etc/my.cnf");
    container.execInContainer("sh", "-c", "sed -i '35 a require_secure_transport=ON' /etc/my.cnf");
    // add client certificates to config file
    if (useAllCertificates) {
      container.execInContainer("sh", "-c", "sed -i '39 a [client]' /etc/mysql/my.cnf");
      container.execInContainer("sh", "-c", "sed -i '40 a ssl-ca=/var/lib/mysql/ca.pem' /etc/my.cnf");
      container.execInContainer("sh", "-c", "sed -i '41 a ssl-cert=/var/lib/mysql/client-cert.pem' /etc/my.cnf");
      container.execInContainer("sh", "-c", "sed -i '42 a ssl-key=/var/lib/mysql/client-key.pem' /etc/my.cnf");
    }
    // copy root certificate and client certificates
    var caCert = container.execInContainer("sh", "-c", "cat /var/lib/mysql/ca.pem").getStdout().trim();

    if (useAllCertificates) {
      var clientKey = container.execInContainer("sh", "-c", "cat /var/lib/mysql/client-key.pem").getStdout().trim();
      var clientCert = container.execInContainer("sh", "-c", "cat /var/lib/mysql/client-cert.pem").getStdout().trim();
      return new Certificate(caCert, clientCert, clientKey);
    } else {
      return new Certificate(caCert);
    }
  }

  public static class Certificate {

    private final String caCertificate;
    private final String clientCertificate;
    private final String clientKey;

    public Certificate(final String caCertificate) {
      this.caCertificate = caCertificate;
      this.clientCertificate = null;
      this.clientKey = null;
    }

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
