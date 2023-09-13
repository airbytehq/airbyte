/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.MongoCatalogHelper.DEFAULT_PRIMARY_KEY;

import autovalue.shaded.com.google.common.collect.Sets;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.MongoUtil;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.ExcludedField;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class MongoDbDebeziumFieldsUtil {

  /**
   * Stream filter that removes the configured primary key field and fields added to the catalog by
   * the metadata injector. These fields should always be included, as they are required to support
   * CDC in the destination. They will be removed from both sides of the set difference calculation to
   * ensure that they are never excluded.
   */
  private static final Predicate<ExcludedField> REQUIRED_FIELDS_FILTER = f -> !f.field().startsWith("_ab") && !f.field().equals(DEFAULT_PRIMARY_KEY);

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
        configuredCatalog.getStreams().stream().map(ConfiguredAirbyteStream::getStream).toList();

    // Get all enabled fields from the configured catalog
    final Set<ExcludedField> fieldsToInclude =
        configuredAirbyteStreams.stream()
            .map(MongoDbDebeziumFieldsUtil::getCollectionAndFields)
            .flatMap(Set::stream)
            .filter(REQUIRED_FIELDS_FILTER)
            .collect(Collectors.toSet());

    // Get all known/discovered fields from the stream
    final Set<ExcludedField> allFields =
        sourceAirbyteStreams.stream()
            .map(MongoDbDebeziumFieldsUtil::getCollectionAndFields)
            .flatMap(Set::stream)
            .filter(REQUIRED_FIELDS_FILTER)
            .collect(Collectors.toSet());

    // Compare the enabled fields to the set of all known fields
    return Sets.difference(allFields, fieldsToInclude);
  }

  private static Set<ExcludedField> getCollectionAndFields(final AirbyteStream stream) {
    return getTopLevelFieldNames(stream).stream()
        .map(fieldName -> new ExcludedField(stream.getNamespace(), stream.getName(), fieldName))
        .collect(Collectors.toSet());
  }

  private static Set<String> getTopLevelFieldNames(final AirbyteStream stream) {
    final Map<String, Object> object = Jsons.object(stream.getJsonSchema().get("properties"), Map.class);
    return object.keySet();
  }

}
