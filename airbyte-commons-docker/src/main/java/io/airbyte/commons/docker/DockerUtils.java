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

package io.airbyte.commons.docker;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.command.BuildImageResultCallback;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;
import com.github.dockerjava.transport.DockerHttpClient;
import java.io.File;
import java.util.Set;

public class DockerUtils {

  private static final DockerClientConfig CONFIG = DefaultDockerClientConfig.createDefaultConfigBuilder().build();
  private static final DockerHttpClient HTTP_CLIENT = new ApacheDockerHttpClient.Builder()
      .dockerHost(CONFIG.getDockerHost())
      .sslConfig(CONFIG.getSSLConfig())
      .maxConnections(100)
      .build();
  private static final DockerClient DOCKER_CLIENT = DockerClientImpl.getInstance(CONFIG, HTTP_CLIENT);

  public static String getTaggedImageName(String dockerRepository, String tag) {
    return String.join(":", dockerRepository, tag);
  }

  public static String buildImage(String dockerFilePath, String tag) {
    return DOCKER_CLIENT.buildImageCmd()
        .withDockerfile(new File(dockerFilePath))
        .withTags(Set.of(tag))
        .exec(new BuildImageResultCallback())
        .awaitImageId();
  }

}
