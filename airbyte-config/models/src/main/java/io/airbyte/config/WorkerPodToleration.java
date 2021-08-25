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

package io.airbyte.config;

import java.util.Objects;

/**
 * Represents a minimal io.fabric8.kubernetes.api.model.Toleration
 */
public class WorkerPodToleration {

  private final String key;
  private final String effect;
  private final String value;
  private final String operator;

  public WorkerPodToleration(String key, String effect, String value, String operator) {
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
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    WorkerPodToleration that = (WorkerPodToleration) o;
    return Objects.equals(key, that.key) && Objects.equals(effect, that.effect)
        && Objects.equals(value, that.value) && Objects.equals(operator,
            that.operator);
  }

  @Override
  public int hashCode() {
    return Objects.hash(key, effect, value, operator);
  }

}
