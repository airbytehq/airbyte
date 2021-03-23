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

package io.airbyte.scheduler.client;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.workers.temporal.TemporalResponse;
import java.util.Objects;
import java.util.UUID;

public class SynchronousResponse<T> {

  private final T output;
  private final SynchronousJobMetadata metadata;

  public static <T> SynchronousResponse<T> error(SynchronousJobMetadata metadata) {
    return new SynchronousResponse<>(null, metadata);
  }

  public static <T> SynchronousResponse<T> success(T output, SynchronousJobMetadata metadata) {
    return new SynchronousResponse<>(output, metadata);
  }

  public static <T> SynchronousResponse<T> fromTemporalResponse(TemporalResponse<T> temporalResponse,
                                                                UUID id,
                                                                ConfigType configType,
                                                                UUID configId,
                                                                long createdAt,
                                                                long endedAt) {

    final SynchronousJobMetadata metadata = SynchronousJobMetadata.fromJobMetadata(
        temporalResponse.getMetadata(),
        id,
        configType,
        configId,
        createdAt,
        endedAt);
    return new SynchronousResponse<>(temporalResponse.getOutput().orElse(null), metadata);
  }

  public SynchronousResponse(final T output, final SynchronousJobMetadata metadata) {
    this.output = output;
    this.metadata = metadata;
  }

  public boolean isSuccess() {
    return metadata.isSucceeded();
  }

  public T getOutput() {
    return output;
  }

  public SynchronousJobMetadata getMetadata() {
    return metadata;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final SynchronousResponse<?> that = (SynchronousResponse<?>) o;
    return Objects.equals(output, that.output) && Objects.equals(metadata, that.metadata);
  }

  @Override
  public int hashCode() {
    return Objects.hash(output, metadata);
  }

  @Override
  public String toString() {
    return "SynchronousResponse{" +
        "output=" + output +
        ", metadata=" + metadata +
        '}';
  }

}
