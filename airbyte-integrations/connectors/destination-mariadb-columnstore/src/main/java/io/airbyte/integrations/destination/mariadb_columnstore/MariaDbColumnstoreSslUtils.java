package io.airbyte.integrations.destination.mariadb_columnstore;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

public class MariaDbColumnstoreSslUtils {

  public static final String PARAM_MODE = "mode";
  public static final String PARAM_CA_CERTIFICATE = "ca_certificate";
  public static final String PARAM_SSL_MODE = "ssl_mode";
  public static final String CONNECTION_PARAM_SSL_MODE = "sslMode";
  public static final String CONNECTION_PARAM_SERVER_SSL_CERT = "serverSslCert";

  public static final String VERIFY_CA = "verify-ca";
  public static final String VERIFY_FULL = "verify-full";
  public static final String TRUST = "trust";
  private static final String CLIENT_CERTIFICATE_PATH = "/etc/ssl/ca.pem";


  public static Map<String, String> handleSslProperties(JsonNode encryption) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (encryption != null && !encryption.isNull()) {
      final var method = encryption.get(PARAM_MODE).asText();
      switch (method) {
        case VERIFY_CA, VERIFY_FULL -> {
          createCaFile(CLIENT_CERTIFICATE_PATH, encryption.get(PARAM_CA_CERTIFICATE).asText());
          additionalParameters.put(CONNECTION_PARAM_SSL_MODE, method);
          additionalParameters.put(CONNECTION_PARAM_SERVER_SSL_CERT, CLIENT_CERTIFICATE_PATH);
        }
        default -> {
          additionalParameters.put(CONNECTION_PARAM_SSL_MODE, method);
        }
      }
    }
    return additionalParameters;
  }

  private static void createCaFile(final String path, final String certificate) {
    try {
      Files.writeString(Paths.get(path),certificate, StandardCharsets.UTF_8);
    } catch (IOException e) {
      throw new RuntimeException("Failed to create CA file", e);
    }
  }

}
