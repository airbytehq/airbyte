/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import autovalue.shaded.com.google.common.collect.Sets;
import com.mongodb.client.MongoClient;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.CollectionAndField;
import io.airbyte.integrations.source.mongodb.internal.MongoUtil;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class MongoDbDebeziumFieldsUtil {

  /**
   * Catalog contains the list of fields to include. In order to get the list of fields to exclude, we
   * need to get the list of all fields in the source database and subtract the list of fields to
   * include.
   */
  public Set<CollectionAndField> getFieldsToExclude(final ConfiguredAirbyteCatalog catalog,
                                                    final String databaseName,
                                                    final MongoClient mongoClient) {
    final List<AirbyteStream> sourceAirbyteStreams = MongoUtil.getAirbyteStreams(mongoClient, databaseName);

    return getFieldsToExclude(
        catalog.getStreams().stream().map(ConfiguredAirbyteStream::getStream).collect(Collectors.toList()), sourceAirbyteStreams);
  }

  private static Set<CollectionAndField> getFieldsToExclude(final List<AirbyteStream> configuredAirbyteStreams,
                                                            final List<AirbyteStream> sourceAirbyteStreams) {
    final Set<CollectionAndField> fieldsToInclude =
        configuredAirbyteStreams.stream().map(MongoDbDebeziumFieldsUtil::getCollectionAndFields).flatMap(Set::stream)
            .collect(Collectors.toSet());

    final Set<CollectionAndField> allFields =
        sourceAirbyteStreams.stream().map(MongoDbDebeziumFieldsUtil::getCollectionAndFields).flatMap(Set::stream)
            .collect(Collectors.toSet());

    return Sets.difference(allFields, fieldsToInclude);
  }

  private static Set<CollectionAndField> getCollectionAndFields(final AirbyteStream stream) {
    return getTopLevelFieldNames(stream).stream().map(fieldName -> new CollectionAndField(stream.getName(), fieldName)).collect(Collectors.toSet());
  }

  private static Set<String> getTopLevelFieldNames(final AirbyteStream stream) {
    final Map<String, Object> object = (Map) io.airbyte.protocol.models.Jsons.object(stream.getJsonSchema().get("properties"), Map.class);
    return object.keySet();
  }

}
