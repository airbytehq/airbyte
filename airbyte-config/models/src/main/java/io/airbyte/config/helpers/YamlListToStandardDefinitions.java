/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
public class YamlListToStandardDefinitions {

  private static final Map<String, String> classNameToIdName = Map.ofEntries(
      new SimpleImmutableEntry<>(StandardDestinationDefinition.class.getCanonicalName(), "destinationDefinitionId"),
      new SimpleImmutableEntry<>(StandardSourceDefinition.class.getCanonicalName(), "sourceDefinitionId"));

  public static List<StandardSourceDefinition> toStandardSourceDefinitions(String yamlStr) throws RuntimeException {
    return verifyAndConvertToModelList(StandardSourceDefinition.class, yamlStr);
  }

  public static List<StandardDestinationDefinition> toStandardDestinationDefinitions(String yamlStr) throws RuntimeException {
    return verifyAndConvertToModelList(StandardDestinationDefinition.class, yamlStr);
  }

  public static JsonNode verifyAndConvertToJsonNode(String idName, String yamlStr) throws RuntimeException {
    final var jsonNode = Yamls.deserialize(yamlStr);
    checkYamlIsPresentWithNoDuplicates(jsonNode, idName);
    return jsonNode;
  }

  @VisibleForTesting
  static <T> List<T> verifyAndConvertToModelList(Class<T> klass, String yamlStr) throws RuntimeException {
    final var jsonNode = Yamls.deserialize(yamlStr);
    final var idName = classNameToIdName.get(klass.getCanonicalName());
    checkYamlIsPresentWithNoDuplicates(jsonNode, idName);
    return toStandardXDefinitions(jsonNode.elements(), klass);
  }

  private static void checkYamlIsPresentWithNoDuplicates(JsonNode deserialize, String idName) throws RuntimeException {
    final var presentDestList = !deserialize.elements().equals(ClassUtil.emptyIterator());
    Preconditions.checkState(presentDestList, "Definition list is empty");
    checkNoDuplicateNames(deserialize.elements());
    checkNoDuplicateIds(deserialize.elements(), idName);
  }

  private static void checkNoDuplicateNames(final Iterator<JsonNode> iter) throws IllegalArgumentException {
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

  private static void checkNoDuplicateIds(final Iterator<JsonNode> fileIterator, final String idName) throws IllegalArgumentException {
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

  private static <T> List<T> toStandardXDefinitions(Iterator<JsonNode> iter, Class<T> c) throws RuntimeException {
    Iterable<JsonNode> iterable = () -> iter;
    var defList = new ArrayList<T>();
    for (JsonNode n : iterable) {
      var def = Jsons.object(n, c);
      defList.add(def);
    }
    return defList;
  }

}
