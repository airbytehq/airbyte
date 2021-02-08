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

package io.airbyte.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;

public class JsonSecretsProcessor {

  public static String AIRBYTE_SECRET_FIELD = "airbyte_secret";

  @VisibleForTesting
  static String SECRETS_MASK = "**********";

  private static String PROPERTIES_FIELD = "properties";

  /**
   * Returns a copy of the input object wherein any fields annotated with "airbyte_secret" in the
   * input schema are masked.
   * <p>
   * TODO this method only masks secrets at the top level of the configuration object. It does not
   * support the keywords anyOf, allOf, oneOf, not, and dependencies. This will be fixed in the
   * future.
   *
   * @param schema Schema containing secret annotations
   * @param obj Object containing potentially secret fields
   * @return
   */
  public JsonNode maskSecrets(JsonNode obj, JsonNode schema) {
    if (!canBeProcessed(schema)) {
      return obj;
    }
    Preconditions.checkArgument(schema.isObject());

    ObjectNode properties = (ObjectNode) schema.get(PROPERTIES_FIELD);
    JsonNode copy = obj.deepCopy();
    for (String key : Jsons.keys(properties)) {
      if (isSecret(properties.get(key)) && copy.has(key)) {
        ((ObjectNode) copy).put(key, SECRETS_MASK);
      }
    }

    return copy;
  }

  /**
   * Returns a copy of the destination object in which any secret fields (as denoted by the input
   * schema) found in the source object are added.
   * <p>
   * TODO this method only absorbs secrets at the top level of the configuration object. It does not
   * support the keywords anyOf, allOf, oneOf, not, and dependencies. This will be fixed in the
   * future.
   *
   * @param src The object potentially containing secrets
   * @param dst The object to absorb secrets into
   * @param schema
   * @return
   */
  public JsonNode copySecrets(JsonNode src, JsonNode dst, JsonNode schema) {
    if (!canBeProcessed(schema)) {
      return dst;
    }
    Preconditions.checkArgument(dst.isObject());
    Preconditions.checkArgument(src.isObject());

    ObjectNode dstCopy = dst.deepCopy();

    ObjectNode properties = (ObjectNode) schema.get(PROPERTIES_FIELD);
    for (String key : Jsons.keys(properties)) {
      // We only copy the original secret if the destination object isn't attempting to overwrite it
      // i.e: if the value of the secret isn't set to the mask
      if (isSecret(properties.get(key)) && src.has(key)) {
        if (dst.has(key) && dst.get(key).asText().equals(SECRETS_MASK))
          dstCopy.set(key, src.get(key));
      }
    }

    return dstCopy;
  }

  private static boolean isSecret(JsonNode obj) {
    return obj.isObject() && obj.has(AIRBYTE_SECRET_FIELD) && obj.get(AIRBYTE_SECRET_FIELD).asBoolean();
  }

  private static boolean canBeProcessed(JsonNode schema) {
    return schema.isObject() && schema.has(PROPERTIES_FIELD) && schema.get(PROPERTIES_FIELD).isObject();
  }

}
