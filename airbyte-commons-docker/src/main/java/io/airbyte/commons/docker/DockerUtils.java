/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
