/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

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

  public AirbyteStreamNameNamespacePair(final String name, final String namespace) {
    this.name = name;
    this.namespace = namespace;
  }

  public String getName() {
    return name;
  }

  public String getNamespace() {
    return namespace;
  }

  /**
   * As this is used as a metrics tag, enforce snake case.
   */
  @Override
  public String toString() {
    return (namespace != null ? namespace : "") + "_" + name;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final AirbyteStreamNameNamespacePair that = (AirbyteStreamNameNamespacePair) o;
    return Objects.equals(name, that.name) && Objects.equals(namespace, that.namespace);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, namespace);
  }

  @Override
  public int compareTo(final AirbyteStreamNameNamespacePair o) {
    if (o == null) {
      return 1;
    }

    // first sort by name
    final int nameCheck = name.compareTo(o.getName());
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

  public static AirbyteStreamNameNamespacePair fromRecordMessage(final AirbyteRecordMessage msg) {
    return new AirbyteStreamNameNamespacePair(msg.getStream(), msg.getNamespace());
  }

  public static AirbyteStreamNameNamespacePair fromAirbyteStream(final AirbyteStream stream) {
    return new AirbyteStreamNameNamespacePair(stream.getName(), stream.getNamespace());
  }

  public static AirbyteStreamNameNamespacePair fromConfiguredAirbyteSteam(final ConfiguredAirbyteStream stream) {
    return fromAirbyteStream(stream.getStream());
  }

  public static Set<AirbyteStreamNameNamespacePair> fromConfiguredCatalog(final ConfiguredAirbyteCatalog catalog) {
    final var pairs = new HashSet<AirbyteStreamNameNamespacePair>();

    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final var pair = fromAirbyteStream(stream.getStream());
      pairs.add(pair);
    }

    return pairs;
  }

}
