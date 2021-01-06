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

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.CaseFormat;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public class MigrationUtils {

  // todo (cgardens) - validate that the JsonNode is in fact JsonSchema.
  /**
   *
   * @param migrationRoot root path of resource files for a given migration migration
   * @param relativePath relative path within the migrationPath to where files for a given type are
   *        found (e.g. config or db).
   * @param schemasToInclude set of which resources to include. other files found in the directory
   *        will be ignored. the common case here is that those other files are referred to by files
   *        that are included here. resolving those dependencies is handled separately.
   * @return map of a path (concatentation of the relativePath and the file name) to the JsonSchema
   *         found there.
   */
  public static Map<Path, JsonNode> getNameToSchemasFromPath(Path migrationRoot, Path relativePath, Set<String> schemasToInclude) {
    final Map<Path, JsonNode> schemas = new HashMap<>();

    final Path pathToSchemas = JsonSchemas.prepareSchemas(migrationRoot.resolve(relativePath).toString(), MigrationV0_11_0.class);
    IOs.listFiles(pathToSchemas)
        .stream()
        .map(f -> JsonSchemaValidator.getSchema(f.toFile()))
        .filter(j -> schemasToInclude.contains(CaseFormat.UPPER_CAMEL.to(CaseFormat.UPPER_UNDERSCORE, j.get("title").asText())))
        .forEach(
            j -> schemas.put(relativePath.resolve(CaseFormat.UPPER_CAMEL.to(CaseFormat.UPPER_UNDERSCORE, j.get("title").asText()) + ".yaml"), j));

    return schemas;
  }

}
