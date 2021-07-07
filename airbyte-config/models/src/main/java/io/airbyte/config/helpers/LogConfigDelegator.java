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

package io.airbyte.config.helpers;

import io.airbyte.config.Configs;

/**
 * Implements {@link LogConfigs} by delegating to a {@link Configs} implementation. Because the
 * logging configuration overlaps with other configuration, this delegation is intended to avoid
 * multiple configurations existing at once.
 */
public class LogConfigDelegator implements LogConfigs {

  private final Configs delegate;

  public LogConfigDelegator(Configs configs) {
    delegate = configs;
  }

  @Override
  public String getS3LogBucket() {
    return delegate.getS3LogBucket();
  }

  @Override
  public String getS3LogBucketRegion() {
    return delegate.getS3LogBucketRegion();
  }

  @Override
  public String getAwsAccessKey() {
    return delegate.getAwsAccessKey();
  }

  @Override
  public String getAwsSecretAccessKey() {
    return delegate.getAwsSecretAccessKey();
  }

  @Override
  public String getS3MinioEndpoint() {
    return delegate.getS3MinioEndpoint();
  }

  @Override
  public String getGcpStorageBucket() {
    return delegate.getGcpStorageBucket();
  }

  @Override
  public String getGoogleApplicationCredentials() {
    return delegate.getGoogleApplicationCredentials();
  }

}
