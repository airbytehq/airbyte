/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config;

import com.google.common.collect.ImmutableMap;
import java.util.Arrays;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * When migrating configs, it is possible that some of the old config types have been removed from
 * the codebase. So we cannot rely on the latest {@link ConfigSchema} to migrate them. This class
 * provides backward compatibility for those legacy config types during migration.
 */
public class ConfigSchemaMigrationSupport {

  // a map from config schema to its id field names
  public static final Map<String, String> CONFIG_SCHEMA_ID_FIELD_NAMES;

  static {
    Map<String, String> currentConfigSchemaIdNames = Arrays.stream(ConfigSchema.values())
        .filter(configSchema -> configSchema.getIdFieldName() != null)
        .collect(Collectors.toMap(Enum::name, ConfigSchema::getIdFieldName));
    CONFIG_SCHEMA_ID_FIELD_NAMES = new ImmutableMap.Builder<String, String>()
        .putAll(currentConfigSchemaIdNames)
        // add removed config schema and its id field names below
        // https://github.com/airbytehq/airbyte/pull/41
        .put("SOURCE_CONNECTION_CONFIGURATION", "sourceSpecificationId")
        .put("DESTINATION_CONNECTION_CONFIGURATION", "destinationSpecificationId")
        // https://github.com/airbytehq/airbyte/pull/528
        .put("SOURCE_CONNECTION_SPECIFICATION", "sourceSpecificationId")
        .put("DESTINATION_CONNECTION_SPECIFICATION", "destinationSpecificationId")
        // https://github.com/airbytehq/airbyte/pull/564
        .put("STANDARD_SOURCE", "sourceId")
        .put("STANDARD_DESTINATION", "destinationId")
        .put("SOURCE_CONNECTION_IMPLEMENTATION", "sourceImplementationId")
        .put("DESTINATION_CONNECTION_IMPLEMENTATION", "destinationImplementationId")
        // https://github.com/airbytehq/airbyte/pull/3472
        .put("STANDARD_SYNC_SCHEDULE", "connectionId")
        .build();
  }

}
