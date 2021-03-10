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
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;

public class SynchronousJobResponse<T> {

  private final T output;
  private final SynchronousJobMetadata metadata;

  public static <T> SynchronousJobResponse<T> error(SynchronousJobMetadata metadata) {
    return new SynchronousJobResponse<>(null, metadata);
  }

  public static <T> SynchronousJobResponse<T> success(T output, SynchronousJobMetadata metadata) {
    return new SynchronousJobResponse<>(output, metadata);
  }

  public SynchronousJobResponse(final T output, final SynchronousJobMetadata metadata) {
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

  public static class SynchronousJobMetadata {

    private final UUID id;
    private final ConfigType configType;
    private final UUID configId;

    private final long createdAt;
    private final long endedAt;
    private final boolean succeeded;

    private final Path logPath;

    public SynchronousJobMetadata(final UUID id,
                                  final ConfigType configType,
                                  final UUID configId,
                                  final long createdAt,
                                  final long endedAt,
                                  final boolean succeeded,
                                  final Path logPath) {
      this.id = id;
      this.configType = configType;
      this.configId = configId;
      this.createdAt = createdAt;
      this.endedAt = endedAt;
      this.succeeded = succeeded;
      this.logPath = logPath;
    }

    public UUID getId() {
      return id;
    }

    public ConfigType getConfigType() {
      return configType;
    }

    public Optional<UUID> getConfigId() {
      return Optional.ofNullable(configId);
    }

    public long getCreatedAt() {
      return createdAt;
    }

    public long getEndedAt() {
      return endedAt;
    }

    public boolean isSucceeded() {
      return succeeded;
    }

    // todo (cgardens) - this should always be present.
    // only present if there was an error.
    public Optional<Path> getLogPath() {
      return Optional.ofNullable(logPath);
    }

  }

}
