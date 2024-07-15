/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.EQUALS;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_PASS;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_TYPE;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_URL;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.TRUST_KEY_STORE_PASS;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.TRUST_KEY_STORE_TYPE;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.TRUST_KEY_STORE_URL;
import static io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialReadUtil.convertNameNamespacePairFromV0;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils;
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbReadUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.singlestore.cursor_based.SingleStoreCursorBasedStateManager;
import io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialLoadHandler;
import io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialLoadStreamStateManager;
import io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialReadUtil;
import io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialReadUtil.CursorBasedStreams;
import io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.singlestore.internal.models.CursorBasedStatus;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreSource extends AbstractJdbcSource<SingleStoreType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreSource.class);
  public static final String DRIVER_CLASS = DatabaseDriver.SINGLESTORE.getDriverClassName();

  public SingleStoreSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new SingleStoreSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final String encodedDatabaseName = URLEncoder.encode(config.get(JdbcUtils.DATABASE_KEY).asText(), StandardCharsets.UTF_8);
    final StringBuilder jdbcUrl = new StringBuilder(
        String.format("jdbc:singlestore://%s:%s/%s", config.get(JdbcUtils.HOST_KEY).asText(), config.get(JdbcUtils.PORT_KEY).asText(),
            encodedDatabaseName));
    jdbcUrl.append("?yearIsDateType=false");
    jdbcUrl.append("&tinyInt1isBit=false");
    // metrics
    jdbcUrl.append(String.format("&_connector_name=%s", "Airbyte Source Connector"));
    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      jdbcUrl.append(JdbcUtils.AMPERSAND).append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }
    final Map<String, String> sslParameters = JdbcSSLConnectionUtils.parseSSLConfig(config);
    jdbcUrl.append(JdbcUtils.AMPERSAND).append(toJDBCQueryParams(sslParameters));
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText()).put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());
    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }
    return Jsons.jsonNode(configBuilder.build());
  }

  /**
   * Generates SSL related query parameters from map of parsed values.
   *
   * @param sslParams ssl parameters
   * @return SSL portion of JDBC question params or and empty string
   */
  public String toJDBCQueryParams(final Map<String, String> sslParams) {
    return Objects.isNull(sslParams) ? "" : sslParams.entrySet().stream().map((entry) -> switch (entry.getKey()) {
      case JdbcSSLConnectionUtils.SSL_MODE -> JdbcSSLConnectionUtils.SSL_MODE + EQUALS
          + com.singlestore.jdbc.export.SslMode.from(entry.getValue()).name();
      case TRUST_KEY_STORE_URL -> "trustStore" + EQUALS + entry.getValue();
      case TRUST_KEY_STORE_PASS -> "trustStorePassword" + EQUALS + entry.getValue();
      case TRUST_KEY_STORE_TYPE -> "trustStoreType" + EQUALS + entry.getValue();
      case CLIENT_KEY_STORE_URL -> "keyStore" + EQUALS + entry.getValue();
      case CLIENT_KEY_STORE_PASS -> "keyStorePassword" + EQUALS + entry.getValue();
      case CLIENT_KEY_STORE_TYPE -> "keyStoreType" + EQUALS + entry.getValue();
      default -> "";
    }).filter(s -> Objects.nonNull(s) && !s.isEmpty()).collect(Collectors.joining(JdbcUtils.AMPERSAND));
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<SingleStoreType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (SingleStoreInitialReadUtil.isAnyStreamIncrementalSyncMode(catalog)) {
      final SingleStoreCursorBasedStateManager cursorBasedStateManager = new SingleStoreCursorBasedStateManager(stateManager.getRawStateMessages(),
          catalog);
      LOGGER.info("Syncing via Primary Key");
      final InitialLoadStreams initialLoadStreams = SingleStoreInitialReadUtil.streamsForInitialPrimaryKeyLoad(stateManager, catalog);
      final Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus = SingleStoreQueryUtils.getCursorBasedSyncStatusForStreams(
          database, initialLoadStreams.streamsForInitialLoad(), stateManager, getQuoteString());
      final CursorBasedStreams cursorBasedStreams = new CursorBasedStreams(
          RelationalDbReadUtil.identifyStreamsForCursorBased(catalog, initialLoadStreams.streamsForInitialLoad()), pairToCursorBasedStatus);

      SingleStoreQueryUtils.logStreamSyncStatus(initialLoadStreams.streamsForInitialLoad(), "Primary Key");
      SingleStoreQueryUtils.logStreamSyncStatus(cursorBasedStreams.streamsForCursorBased(), "Cursor");

      final SingleStoreInitialLoadStreamStateManager singleStoreInitialLoadStreamStateManager = new SingleStoreInitialLoadStreamStateManager(
          initialLoadStreams,
          SingleStoreInitialReadUtil.initPairToPrimaryKeyInfoMap(database, initialLoadStreams, tableNameToTable, getQuoteString()));
      final SingleStoreInitialLoadHandler initialLoadHandler = new SingleStoreInitialLoadHandler(sourceConfig, database,
          new SingleStoreSourceOperations(), getQuoteString(), singleStoreInitialLoadStreamStateManager,
          namespacePair -> Jsons.jsonNode(pairToCursorBasedStatus.get(convertNameNamespacePairFromV0(namespacePair))));
      final List<AutoCloseableIterator<AirbyteMessage>> initialLoadIterator = new ArrayList<>(
          initialLoadHandler.getIncrementalIterators(new ConfiguredAirbyteCatalog().withStreams(initialLoadStreams.streamsForInitialLoad()),
              tableNameToTable, emittedAt));

      // Build Cursor based iterator
      final List<AutoCloseableIterator<AirbyteMessage>> cursorBasedIterator = new ArrayList<>(
          super.getIncrementalIterators(database, new ConfiguredAirbyteCatalog().withStreams(cursorBasedStreams.streamsForCursorBased()),
              tableNameToTable, cursorBasedStateManager, emittedAt));
      return Stream.of(initialLoadIterator, cursorBasedIterator).flatMap(Collection::stream).collect(Collectors.toList());
    }
    return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of("information_schema", "memsql", "cluster");
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new SingleStoreSource();
    LOGGER.info("starting source: {}", SingleStoreSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", SingleStoreSource.class);
  }

}
