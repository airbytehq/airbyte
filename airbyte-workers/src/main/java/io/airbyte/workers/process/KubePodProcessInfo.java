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

package io.airbyte.workers.process;

import java.lang.ProcessHandle.Info;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;

/**
 * Minimal Process info implementation to assist with debug logging.
 *
 * Current implement only logs out the Kubernetes pod corresponding to the JVM process.
 */
public class KubePodProcessInfo implements Info {

  private final String podName;

  public KubePodProcessInfo(String podname) {
    this.podName = podname;
  }

  @Override
  public Optional<String> command() {
    return Optional.of(podName);
  }

  @Override
  public Optional<String> commandLine() {
    return Optional.of(podName);
  }

  @Override
  public Optional<String[]> arguments() {
    return Optional.empty();
  }

  @Override
  public Optional<Instant> startInstant() {
    return Optional.empty();
  }

  @Override
  public Optional<Duration> totalCpuDuration() {
    return Optional.empty();
  }

  @Override
  public Optional<String> user() {
    return Optional.empty();
  }

}
