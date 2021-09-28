/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.CaseFormat;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.commons.json.Jsons;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.nio.file.Path;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;

public class MigrationUtils {

  // todo (cgardens) - validate that the JsonNode is in fact JsonSchema.
  /**
   *
   * @param migrationResourcePath root path of resource files for a given migration migration
   * @param relativePath relative path within the migrationPath to where files for a given type are
   *        found (e.g. config or db).
   * @param schemasToInclude set of which resources to include. other files found in the directory
   *        will be ignored. the common case here is that those other files are referred to by files
   *        that are included here. resolving those dependencies is handled separately.
   * @return ResourceId to the JsonSchema found there.
   */
  public static Map<ResourceId, JsonNode> getNameToSchemasFromResourcePath(Path migrationResourcePath,
                                                                           Path relativePath,
                                                                           ResourceType resourceType,
                                                                           Set<String> schemasToInclude) {
    return getNameToSchemasFromResourcePath(migrationResourcePath.resolve(relativePath), resourceType, schemasToInclude);
  }

  public static Map<ResourceId, JsonNode> getNameToSchemasFromResourcePath(Path pathToSchemasResource,
                                                                           ResourceType resourceType,
                                                                           Set<String> schemasToInclude) {
    final Map<ResourceId, JsonNode> schemas = new HashMap<>();
    final Path pathToSchemas = JsonSchemas.prepareSchemas(pathToSchemasResource.toString(), MigrationUtils.class);
    FileUtils.listFiles(pathToSchemas.toFile(), null, false)
        .stream()
        .map(JsonSchemaValidator::getSchema)
        .filter(j -> schemasToInclude.contains(getTitleAsConstantCase(j)))
        .forEach(j -> {
          final ResourceId resourceId = ResourceId.fromConstantCase(resourceType, getTitleAsConstantCase(j));
          schemas.put(resourceId, j);
        });

    return schemas;
  }

  // this method is decently inefficient. if you need to fetch the schema for multiple configs, use
  // getNameToSchemasFromResourcePath.
  public static JsonNode getSchemaFromResourcePath(Path pathToSchema, ResourceId resourceId) {
    final Map<ResourceId, JsonNode> nameToSchemas = getNameToSchemasFromResourcePath(
        pathToSchema,
        resourceId.getType(),
        Collections.singleton(resourceId.getName()));
    return nameToSchemas.get(resourceId);
  }

  private static String getTitleAsConstantCase(JsonNode jsonNode) {
    return CaseFormat.UPPER_CAMEL.to(CaseFormat.UPPER_UNDERSCORE, jsonNode.get("title").asText());
  }

  public static Map<ResourceId, JsonNode> getConfigModels(Path migrationResourcePath, Set<String> schemasToInclude) {
    return getNameToSchemasFromResourcePath(migrationResourcePath, ResourceType.CONFIG.getDirectoryName(), ResourceType.CONFIG, schemasToInclude);
  }

  public static Map<ResourceId, JsonNode> getJobModels(Path migrationResourcePath, Set<String> schemasToInclude) {
    return getNameToSchemasFromResourcePath(migrationResourcePath, ResourceType.JOB.getDirectoryName(), ResourceType.JOB, schemasToInclude);
  }

  /**
   * Insert new records in @param metadataTable table to keep track that a migration was applied to
   * the set of Resources in @param outputData. After applying this migration successfully, such
   * resource files are now upgraded and compatible with Airbyte @param version
   */
  public static void registerMigrationRecord(final Map<ResourceId, Consumer<JsonNode>> outputData, final String metadataTable, final String version) {
    final ResourceId resourceId = ResourceId.fromConstantCase(ResourceType.JOB, metadataTable);
    final Consumer<JsonNode> metadataOutputConsumer = outputData.get(resourceId);
    metadataOutputConsumer.accept(Jsons.jsonNode(ImmutableMap.of(
        "key", String.format("%s_migrate_to", current_timestamp()),
        "value", version)));
  }

  public static String current_timestamp() {
    return ZonedDateTime.now().format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
  }

  public static Map<ResourceId, Consumer<JsonNode>> mapRecordConsumerToConsumer(Map<ResourceId, ? extends Consumer<JsonNode>> recordConsumers) {
    return recordConsumers.entrySet()
        .stream()
        .collect(Collectors.toMap(Entry::getKey, e -> (v) -> e.getValue().accept(v)));
  }

}
