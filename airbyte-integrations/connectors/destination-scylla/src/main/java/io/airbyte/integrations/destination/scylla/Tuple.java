/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

public class Tuple<V1, V2> {

  private final V1 value1;

  private final V2 value2;

  public Tuple(V1 value1, V2 value2) {
    this.value1 = value1;
    this.value2 = value2;
  }

  public static <V1, V2> Tuple<V1, V2> of(V1 value1, V2 value2) {
    return new Tuple<>(value1, value2);
  }

  public V1 value1() {
    return value1;
  }

  public V2 value2() {
    return value2;
  }

  @Override
  public String toString() {
    return "Tuple{" +
        "value1=" + value1 +
        ", value2=" + value2 +
        '}';
  }

}
