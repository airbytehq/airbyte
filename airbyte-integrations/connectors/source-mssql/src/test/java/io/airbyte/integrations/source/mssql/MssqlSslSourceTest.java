/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.CertificateKey;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import java.net.InetAddress;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSslSourceTest {

  private MsSQLTestDatabase testDb;
  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSslSourceTest.class);

  @BeforeEach
  void setup() {
    testDb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022, ContainerModifier.AGENT, ContainerModifier.WITH_SSL_CERTIFICATES);
  }

  @AfterEach
  public void tearDown() {
    testDb.close();
  }

  @ParameterizedTest
  @EnumSource(CertificateKey.class)
  public void testDiscoverWithCertificateTrustHostnameWithValidCertificates(CertificateKey certificateKey) throws Exception {
    if (!certificateKey.isValid) {
      return;
    }
    String certificate = testDb.getCertificate(certificateKey);
    JsonNode config = testDb.testConfigBuilder()
        .withSsl(Map.of("ssl_method", "encrypted_verify_certificate",
            "certificate", certificate))
        .build();
    AirbyteCatalog catalog = new MssqlSource().discover(config);
  }

  @ParameterizedTest
  @EnumSource(CertificateKey.class)
  public void testDiscoverWithCertificateTrustHostnameWithInvalidCertificates(CertificateKey certificateKey) throws Exception {
    if (certificateKey.isValid) {
      return;
    }
    String certificate = testDb.getCertificate(certificateKey);
    JsonNode config = testDb.testConfigBuilder()
        .withSsl(Map.of("ssl_method", "encrypted_verify_certificate",
            "certificate", certificate))
        .build();
    try {
      AirbyteCatalog catalog = new MssqlSource().discover(config);
    } catch (ConnectionErrorException e) {
      if (!e.getCause().getCause().getMessage().contains("PKIX path validation") &&
          !e.getCause().getCause().getMessage().contains("PKIX path building failed")) {
        throw e;
      }
    }
  }

  @ParameterizedTest
  @EnumSource(CertificateKey.class)
  public void testDiscoverWithCertificateNoTrustHostnameWrongHostname(CertificateKey certificateKey) throws Throwable {
    if (!certificateKey.isValid) {
      return;
    }
    String containerIp = InetAddress.getByName(testDb.getContainer().getHost()).getHostAddress();
    String certificate = testDb.getCertificate(certificateKey);
    JsonNode config = testDb.configBuilder()
        .withSsl(Map.of("ssl_method", "encrypted_verify_certificate",
            "certificate", certificate))
        .with(JdbcUtils.HOST_KEY, containerIp)
        .with(JdbcUtils.PORT_KEY, testDb.getContainer().getFirstMappedPort())
        .withCredentials()
        .withDatabase()
        .build();
    try {
      AirbyteCatalog catalog = new MssqlSource().discover(config);
      fail("discover should have failed!");
    } catch (ConnectionErrorException e) {
      String expectedMessage =
          "Failed to validate the server name \"" + containerIp + "\"in a certificate during Secure Sockets Layer (SSL) initialization.";
      if (!e.getExceptionMessage().contains(expectedMessage)) {
        fail("exception message was " + e.getExceptionMessage() + "\n expected: " + expectedMessage);
      }
    }
  }

  @ParameterizedTest
  @EnumSource(CertificateKey.class)
  public void testDiscoverWithCertificateNoTrustHostnameAlternateHostname(CertificateKey certificateKey) throws Exception {
    final String containerIp = InetAddress.getByName(testDb.getContainer().getHost()).getHostAddress();
    if (certificateKey.isValid) {
      String certificate = testDb.getCertificate(certificateKey);
      JsonNode config = testDb.configBuilder()
          .withSsl(Map.of("ssl_method", "encrypted_verify_certificate",
              "certificate", certificate,
              "hostNameInCertificate", testDb.getContainer().getHost()))
          .with(JdbcUtils.HOST_KEY, containerIp)
          .with(JdbcUtils.PORT_KEY, testDb.getContainer().getFirstMappedPort())
          .withCredentials()
          .withDatabase()
          .build();
      AirbyteCatalog catalog = new MssqlSource().discover(config);
    }
  }

}
