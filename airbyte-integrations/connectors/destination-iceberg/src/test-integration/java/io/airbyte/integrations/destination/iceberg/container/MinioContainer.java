/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.container;

import java.time.Duration;
import java.util.List;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.HttpWaitStrategy;

/**
 * @author Leibniz on 2022/11/3.
 */
public class MinioContainer extends GenericContainer<MinioContainer> {

  public static final String DEFAULT_ACCESS_KEY = "DEFAULT_ACCESS_KEY";
  public static final String DEFAULT_SECRET_KEY = "DEFAULT_SECRET_KEY";

  public static final int MINIO_PORT = 9000;
  private static final String DEFAULT_IMAGE = "minio/minio";
  private static final String DEFAULT_TAG = "edge";

  private static final String MINIO_ACCESS_KEY = "MINIO_ACCESS_KEY";
  private static final String MINIO_SECRET_KEY = "MINIO_SECRET_KEY";

  private static final String DEFAULT_STORAGE_DIRECTORY = "/data";
  public static final String HEALTH_ENDPOINT = "/minio/health/ready";

  public MinioContainer() {
    this(DEFAULT_IMAGE + ":" + DEFAULT_TAG, null, null);
  }

  public MinioContainer(CredentialsProvider credentials) {
    this(DEFAULT_IMAGE + ":" + DEFAULT_TAG, credentials, null);
  }

  public MinioContainer(String image, CredentialsProvider credentials, Integer bindPort) {
    super(image == null ? DEFAULT_IMAGE + ":" + DEFAULT_TAG : image);
    addExposedPort(MINIO_PORT);
    if (credentials != null) {
      withEnv(MINIO_ACCESS_KEY, credentials.getAccessKey());
      withEnv(MINIO_SECRET_KEY, credentials.getSecretKey());
    }
    withCommand("server", DEFAULT_STORAGE_DIRECTORY);
    setWaitStrategy(new HttpWaitStrategy()
        .forPort(MINIO_PORT)
        .forPath(HEALTH_ENDPOINT)
        .withStartupTimeout(Duration.ofMinutes(2)));
    if (bindPort != null) {
      setPortBindings(List.of(bindPort + ":" + MINIO_PORT));
    }
  }

  public String getHostAddress() {
    return getContainerIpAddress() + ":" + getMappedPort(MINIO_PORT);
  }

  public int getPort() {
    return getMappedPort(MINIO_PORT);
  }

  public static class CredentialsProvider {

    private final String accessKey;
    private final String secretKey;

    public CredentialsProvider(String accessKey, String secretKey) {
      this.accessKey = accessKey;
      this.secretKey = secretKey;
    }

    public String getAccessKey() {
      return accessKey;
    }

    public String getSecretKey() {
      return secretKey;
    }

  }

}
