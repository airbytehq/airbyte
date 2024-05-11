/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import io.airbyte.commons.json.Jsons;
import io.debezium.connector.mongodb.MongoDbConnectorConfig;
import io.debezium.connector.mongodb.MongoDbOffsetContext;
import io.debezium.connector.mongodb.MongoDbOffsetContext.Loader;
import io.debezium.connector.mongodb.ReplicaSets;
import java.util.Collections;
import java.util.Map;

/**
 * Custom Debezium offset loader for MongoDB.
 * <p />
 * <p />
 * N.B. In order to extract the offset from the {@link MongoDbCustomLoader}, you must first get the
 * {@link io.debezium.connector.mongodb.ReplicaSetOffsetContext} from the
 * {@link MongoDbOffsetContext} for the replica set for which the offset is requested. From that
 * context, you can then request the actual Debezium offset.
 */
public class MongoDbCustomLoader extends Loader {

  private Map<Map<String, String>, Map<String, Object>> offsets;

  public MongoDbCustomLoader(final MongoDbConnectorConfig connectorConfig, final ReplicaSets replicaSets) {
    super(connectorConfig, replicaSets);
  }

  @Override
  public MongoDbOffsetContext loadOffsets(final Map<Map<String, String>, Map<String, Object>> offsets) {
    this.offsets = Jsons.clone(offsets);
    return super.loadOffsets(offsets);
  }

  public Map<Map<String, String>, Map<String, Object>> getRawOffset() {
    return Collections.unmodifiableMap(offsets);
  }

}
