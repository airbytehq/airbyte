/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

public class Triplet<V1, V2, V3> {

  private final V1 value1;

  private final V2 value2;

  private final V3 value3;

  public Triplet(V1 value1, V2 value2, V3 value3) {
    this.value1 = value1;
    this.value2 = value2;
    this.value3 = value3;
  }

  public static <V1, V2, V3> Triplet<V1, V2, V3> of(V1 value1, V2 value2, V3 value3) {
    return new Triplet<>(value1, value2, value3);
  }

  public V1 value1() {
    return value1;
  }

  public V2 value2() {
    return value2;
  }

  public V3 value3() {
    return value3;
  }

  @Override
  public String toString() {
    return "Triplet{" +
        "value1=" + value1 +
        ", value2=" + value2 +
        ", value3=" + value3 +
        '}';
  }

}
