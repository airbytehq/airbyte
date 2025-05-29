/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.container;

import java.time.Duration;
import java.util.List;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.HttpWaitStrategy;

/**
 * @author Leibniz on 2022/11/3.
 */
// TODO: Delete this class after deleting HiveMetastore related test classes
public class MinioContainerOldToDelete extends GenericContainer<MinioContainerOldToDelete> {

  public static final String DEFAULT_ACCESS_KEY = "DEFAULT_ACCESS_KEY";
  public static final String DEFAULT_SECRET_KEY = "DEFAULT_SECRET_KEY";

  public static final int DEFAULT_PORT = 9000;
  private static final String DEFAULT_IMAGE = "minio/minio";
  private static final String DEFAULT_TAG = "edge";

  private static final String MINIO_ACCESS_KEY = "MINIO_ACCESS_KEY";
  private static final String MINIO_SECRET_KEY = "MINIO_SECRET_KEY";

  private static final String DEFAULT_STORAGE_DIRECTORY = "/data";
  public static final String HEALTH_ENDPOINT = "/minio/health/ready";

  public MinioContainerOldToDelete(String image, CredentialsProvider credentials, Integer bindPort) {
    super(image == null ? DEFAULT_IMAGE + ":" + DEFAULT_TAG : image);
    addExposedPort(DEFAULT_PORT);
    if (credentials != null) {
      withEnv(MINIO_ACCESS_KEY, credentials.accessKey());
      withEnv(MINIO_SECRET_KEY, credentials.secretKey());
    }
    withCommand("server", DEFAULT_STORAGE_DIRECTORY);
    setWaitStrategy(new HttpWaitStrategy()
        .forPort(DEFAULT_PORT)
        .forPath(HEALTH_ENDPOINT)
        .withStartupTimeout(Duration.ofMinutes(2)));
    if (bindPort != null) {
      setPortBindings(List.of(bindPort + ":" + DEFAULT_PORT));
    }
  }

  public String getHostAddress() {
    return getContainerIpAddress() + ":" + getMappedPort(DEFAULT_PORT);
  }

  public record CredentialsProvider(String accessKey, String secretKey) {}

}
