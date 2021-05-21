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
