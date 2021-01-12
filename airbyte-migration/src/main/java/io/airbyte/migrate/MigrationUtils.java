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

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.CaseFormat;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
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
  private static Map<ResourceId, JsonNode> getNameToSchemasFromPath(Path migrationResourcePath,
                                                                    Path relativePath,
                                                                    ResourceType resourceType,
                                                                    Set<String> schemasToInclude) {
    final Map<ResourceId, JsonNode> schemas = new HashMap<>();
    final Path pathToSchemas = JsonSchemas.prepareSchemas(migrationResourcePath.resolve(relativePath).toString(), MigrationUtils.class);
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

  private static String getTitleAsConstantCase(JsonNode jsonNode) {
    return CaseFormat.UPPER_CAMEL.to(CaseFormat.UPPER_UNDERSCORE, jsonNode.get("title").asText());
  }

  public static Map<ResourceId, JsonNode> getConfigModels(Path migrationResourcePath, Set<String> schemasToInclude) {
    return getNameToSchemasFromPath(migrationResourcePath, ResourceType.CONFIG.getDirectoryName(), ResourceType.CONFIG, schemasToInclude);
  }

  public static Map<ResourceId, JsonNode> getJobModels(Path migrationResourcePath, Set<String> schemasToInclude) {
    return getNameToSchemasFromPath(migrationResourcePath, ResourceType.JOB.getDirectoryName(), ResourceType.JOB, schemasToInclude);
  }

}
