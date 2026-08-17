/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.documentdb;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.ConnectionString;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.mongodb.MongodbDestination;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

public class DocumentDbDestination extends MongodbDestination {

  @Override
  protected String getConnectionString(final JsonNode config) {
    return buildConnectionString(config);
  }

  static String buildConnectionString(final JsonNode config) {
    final String uri = config.hasNonNull("connection_string")
        ? config.get("connection_string").asText().trim()
        : String.format("mongodb://%s:%d/", config.get("host").asText(), config.path("port").asInt(10260));
    if (!uri.startsWith("mongodb://")) {
      throw new IllegalArgumentException("DocumentDB connection strings must use the mongodb:// scheme.");
    }
    final ConnectionString parsed = new ConnectionString(uri);
    final StringBuilder result = new StringBuilder("mongodb://");
    if (config.hasNonNull("username") && config.hasNonNull("password")) {
      result.append(URLEncoder.encode(config.get("username").asText(), StandardCharsets.UTF_8))
          .append(':').append(URLEncoder.encode(config.get("password").asText(), StandardCharsets.UTF_8)).append('@');
    } else if (uri.substring("mongodb://".length()).contains("@")) {
      result.append(uri, "mongodb://".length(), uri.indexOf('@') + 1);
    }
    result.append(String.join(",", parsed.getHosts())).append('/').append(config.get("database").asText())
        .append("?retryWrites=false")
        .append("&tls=").append(config.path("tls").asBoolean(true))
        .append("&directConnection=").append(config.path("direct_connection").asBoolean(parsed.getHosts().size() == 1))
        .append("&readPreference=").append(config.path("read_preference").asText("primaryPreferred"))
        .append("&authSource=").append(config.path("auth_source").asText("admin"));
    if (config.hasNonNull("replica_set") && !config.get("replica_set").asText().isBlank()) {
      result.append("&replicaSet=").append(config.get("replica_set").asText());
    }
    return result.toString();
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new DocumentDbDestination()).run(args);
  }
}