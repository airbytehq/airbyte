/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.documentdb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.MongoCredential;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.mongodb.MongoDbSource;
import io.airbyte.integrations.source.mongodb.MongoDbSourceConfig;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class DocumentDbSource extends MongoDbSource {

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final JsonNode normalized = normalizeConfig(config);
      final MongoDbSourceConfig sourceConfig = new MongoDbSourceConfig(normalized);
      try (MongoClient client = createMongoClient(sourceConfig)) {
        for (String database : sourceConfig.getDatabaseNames()) {
          client.getDatabase(database).listCollectionNames().first();
        }
      }
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    final AirbyteCatalog catalog = super.discover(normalizeConfig(config));
    catalog.getStreams().forEach(stream -> stream
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH))
        .withSourceDefinedCursor(false)
        .withDefaultCursorField(List.of()));
    return catalog;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state) {
    if (catalog.getStreams().stream().anyMatch(stream -> stream.getSyncMode() != SyncMode.FULL_REFRESH)) {
      throw new IllegalArgumentException("DocumentDB source supports full refresh syncs only.");
    }
    return super.read(normalizeConfig(config), catalog, state);
  }

  @Override
  protected MongoClient createMongoClient(final MongoDbSourceConfig config) {
    final ConnectionString connectionString = new ConnectionString(config.getDatabaseConfig().get("connection_string").asText());
    final MongoClientSettings.Builder settings = MongoClientSettings.builder().applyConnectionString(connectionString);
    if (config.hasAuthCredentials()) {
      settings.credential(MongoCredential.createCredential(config.getUsername(), config.getAuthSource(), config.getPassword().toCharArray()));
    }
    return MongoClients.create(settings.build());
  }

  static JsonNode normalizeConfig(final JsonNode config) {
    final ObjectNode normalized = Jsons.clone(config).deepCopy();
    final ObjectNode databaseConfig = normalized.putObject("database_config");
    databaseConfig.put("cluster_type", "SELF_MANAGED_REPLICA_SET");
    databaseConfig.put("connection_string", buildConnectionString(config));
    databaseConfig.set("databases", config.get("databases"));
    databaseConfig.put("schema_enforced", config.path("schema_enforced").asBoolean(true));
    if (config.hasNonNull("username"))
      databaseConfig.set("username", config.get("username"));
    if (config.hasNonNull("password"))
      databaseConfig.set("password", config.get("password"));
    databaseConfig.put("auth_source", config.path("auth_source").asText("admin"));
    return normalized;
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
    result.append(String.join(",", parsed.getHosts())).append("/?retryWrites=false")
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
    new IntegrationRunner(new DocumentDbSource()).run(args);
  }

}
