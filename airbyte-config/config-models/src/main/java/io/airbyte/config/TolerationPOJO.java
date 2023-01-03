/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import java.util.Objects;

/**
 * Represents a minimal io.fabric8.kubernetes.api.model.Toleration
 */
@SuppressWarnings("PMD.ShortVariable")
public class TolerationPOJO {

  private final String key;
  private final String effect;
  private final String value;
  private final String operator;

  public TolerationPOJO(final String key, final String effect, final String value, final String operator) {
    this.key = key;
    this.effect = effect;
    this.value = value;
    this.operator = operator;
  }

  public String getKey() {
    return key;
  }

  public String getEffect() {
    return effect;
  }

  public String getValue() {
    return value;
  }

  public String getOperator() {
    return operator;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final TolerationPOJO that = (TolerationPOJO) o;
    return Objects.equals(key, that.key) && Objects.equals(effect, that.effect)
        && Objects.equals(value, that.value) && Objects.equals(operator,
            that.operator);
  }

  @Override
  public int hashCode() {
    return Objects.hash(key, effect, value, operator);
  }

}
