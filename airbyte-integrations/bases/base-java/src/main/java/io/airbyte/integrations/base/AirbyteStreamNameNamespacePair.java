/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

/**
 * Wraps an {@link io.airbyte.protocol.models.AirbyteStream}'s name and namespace fields to simplify
 * comparison checks. This is helpful since these two fields are often used as an Airbyte Stream's
 * unique identifiers.
 */
public class AirbyteStreamNameNamespacePair implements Comparable<AirbyteStreamNameNamespacePair> {

  final private String name;
  final private String namespace;

  public AirbyteStreamNameNamespacePair(String name, String namespace) {
    this.name = name;
    this.namespace = namespace;
  }

  public String getName() {
    return name;
  }

  public String getNamespace() {
    return namespace;
  }

  @Override
  public String toString() {
    return "AirbyteStreamNameNamespacePair{" +
        "name='" + name + '\'' +
        ", namespace='" + namespace + '\'' +
        '}';
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    AirbyteStreamNameNamespacePair that = (AirbyteStreamNameNamespacePair) o;
    return Objects.equals(name, that.name) && Objects.equals(namespace, that.namespace);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, namespace);
  }

  @Override
  public int compareTo(AirbyteStreamNameNamespacePair o) {
    if (o == null) {
      return 1;
    }

    // first sort by name
    int nameCheck = name.compareTo(o.getName());
    if (nameCheck != 0) {
      return nameCheck;
    }

    // then sort by namespace
    if (namespace == null && o.getNamespace() == null) {
      return 0;
    }
    if (namespace == null && o.getNamespace() != null) {
      return -1;
    }
    if (namespace != null && o.getNamespace() == null) {
      return 1;
    }
    return namespace.compareTo(o.getNamespace());
  }

  public static void main(String[] args) {
    System.out.println("test".compareTo(null));
  }

  public static AirbyteStreamNameNamespacePair fromRecordMessage(AirbyteRecordMessage msg) {
    return new AirbyteStreamNameNamespacePair(msg.getStream(), msg.getNamespace());
  }

  public static AirbyteStreamNameNamespacePair fromAirbyteSteam(AirbyteStream stream) {
    return new AirbyteStreamNameNamespacePair(stream.getName(), stream.getNamespace());
  }

  public static AirbyteStreamNameNamespacePair fromConfiguredAirbyteSteam(ConfiguredAirbyteStream stream) {
    return fromAirbyteSteam(stream.getStream());
  }

  public static Set<AirbyteStreamNameNamespacePair> fromConfiguredCatalog(ConfiguredAirbyteCatalog catalog) {
    var pairs = new HashSet<AirbyteStreamNameNamespacePair>();

    for (ConfiguredAirbyteStream stream : catalog.getStreams()) {
      var pair = fromAirbyteSteam(stream.getStream());
      pairs.add(pair);
    }

    return pairs;
  }

}
