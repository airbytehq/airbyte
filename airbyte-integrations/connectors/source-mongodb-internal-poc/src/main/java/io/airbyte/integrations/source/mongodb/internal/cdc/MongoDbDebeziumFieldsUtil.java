/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import autovalue.shaded.com.google.common.collect.Sets;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import io.airbyte.integrations.source.mongodb.internal.MongoUtil;
import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.ExcludedField;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class MongoDbDebeziumFieldsUtil {

  /**
   * Catalog contains the list of fields to include. In order to get the list of fields not included
   * in the configuredCatalog, we need to get the list of all fields in the source database and
   * subtract the list of fields in the configuredCatalog
   */
  public Set<ExcludedField> getFieldsNotIncludedInCatalog(final ConfiguredAirbyteCatalog configuredCatalog,
                                                          final String databaseName,
                                                          final MongoClient mongoClient) {
    final List<AirbyteStream> sourceAirbyteStreams = MongoUtil.getAirbyteStreams(mongoClient, databaseName);

    return getFieldsNotIncludedInConfiguredStreams(configuredCatalog, sourceAirbyteStreams);
  }

  @VisibleForTesting
  static Set<ExcludedField> getFieldsNotIncludedInConfiguredStreams(final ConfiguredAirbyteCatalog configuredCatalog,
                                                                    final List<AirbyteStream> sourceAirbyteStreams) {

    final List<AirbyteStream> configuredAirbyteStreams =
        configuredCatalog.getStreams().stream().map(ConfiguredAirbyteStream::getStream).collect(Collectors.toList());
    final Set<ExcludedField> fieldsToInclude =
        configuredAirbyteStreams.stream().map(MongoDbDebeziumFieldsUtil::getCollectionAndFields).flatMap(Set::stream)
            .collect(Collectors.toSet());

    final Set<ExcludedField> allFields =
        sourceAirbyteStreams.stream().map(MongoDbDebeziumFieldsUtil::getCollectionAndFields).flatMap(Set::stream)
            .collect(Collectors.toSet());

    return Sets.difference(allFields, fieldsToInclude);
  }

  private static Set<ExcludedField> getCollectionAndFields(final AirbyteStream stream) {
    return getTopLevelFieldNames(stream).stream().map(fieldName -> new ExcludedField(stream.getNamespace(), stream.getName(), fieldName))
        .collect(Collectors.toSet());
  }

  private static Set<String> getTopLevelFieldNames(final AirbyteStream stream) {
    final Map<String, Object> object = (Map) io.airbyte.protocol.models.Jsons.object(stream.getJsonSchema().get("properties"), Map.class);
    return object.keySet();
  }

}
