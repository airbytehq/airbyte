/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.util.ClassUtil;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import java.util.AbstractMap.SimpleImmutableEntry;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/**
 * This is a convenience class for the conversion of a list of source/destination definitions from
 * human-friendly yaml to processing friendly formats i.e. Java models or JSON. As this class
 * performs validation, it is recommended to use this class to deal with plain lists. An example of
 * such lists are Airbyte's master definition lists, which can be seen in the resources folder of
 * the airbyte-config/seed module.
 *
 * In addition to usual deserialization validations, we check: 1) The given list contains no
 * duplicate names. 2) The given list contains no duplicate ids.
 *
 * Methods in these class throw Runtime exceptions upon validation failure.
 */
@SuppressWarnings("PMD.ShortVariable")
public class YamlListToStandardDefinitions {

  private static final Map<String, String> CLASS_NAME_TO_ID_NAME = Map.ofEntries(
      new SimpleImmutableEntry<>(StandardDestinationDefinition.class.getCanonicalName(), "destinationDefinitionId"),
      new SimpleImmutableEntry<>(StandardSourceDefinition.class.getCanonicalName(), "sourceDefinitionId"));

  public static List<StandardSourceDefinition> toStandardSourceDefinitions(final String yamlStr) {
    return verifyAndConvertToModelList(StandardSourceDefinition.class, yamlStr);
  }

  public static List<StandardDestinationDefinition> toStandardDestinationDefinitions(final String yamlStr) {
    return verifyAndConvertToModelList(StandardDestinationDefinition.class, yamlStr);
  }

  public static JsonNode verifyAndConvertToJsonNode(final String idName, final String yamlStr) {
    final var jsonNode = Yamls.deserialize(yamlStr);
    checkYamlIsPresentWithNoDuplicates(jsonNode, idName);
    return jsonNode;
  }

  @VisibleForTesting
  static <T> List<T> verifyAndConvertToModelList(final Class<T> klass, final String yamlStr) {
    final var jsonNode = Yamls.deserialize(yamlStr);
    final var idName = CLASS_NAME_TO_ID_NAME.get(klass.getCanonicalName());
    checkYamlIsPresentWithNoDuplicates(jsonNode, idName);
    return toStandardXDefinitions(jsonNode.elements(), klass);
  }

  private static void checkYamlIsPresentWithNoDuplicates(final JsonNode deserialize, final String idName) {
    final var presentDestList = !deserialize.elements().equals(ClassUtil.emptyIterator());
    Preconditions.checkState(presentDestList, "Definition list is empty");
    checkNoDuplicateNames(deserialize.elements());
    checkNoDuplicateIds(deserialize.elements(), idName);
  }

  private static void checkNoDuplicateNames(final Iterator<JsonNode> iter) {
    final var names = new HashSet<String>();
    while (iter.hasNext()) {
      final var element = Jsons.clone(iter.next());
      final var name = element.get("name").asText();
      if (names.contains(name)) {
        throw new IllegalArgumentException("Multiple records have the name: " + name);
      }
      names.add(name);
    }
  }

  private static void checkNoDuplicateIds(final Iterator<JsonNode> fileIterator, final String idName) {
    final var ids = new HashSet<String>();
    while (fileIterator.hasNext()) {
      final var element = Jsons.clone(fileIterator.next());
      final var id = element.get(idName).asText();
      if (ids.contains(id)) {
        throw new IllegalArgumentException("Multiple records have the id: " + id);
      }
      ids.add(id);
    }
  }

  private static <T> List<T> toStandardXDefinitions(final Iterator<JsonNode> iter, final Class<T> c) {
    final Iterable<JsonNode> iterable = () -> iter;
    final var defList = new ArrayList<T>();
    for (final JsonNode n : iterable) {
      final var def = Jsons.object(n, c);
      defList.add(def);
    }
    return defList;
  }

}
