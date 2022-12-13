/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.secretsmanager.caching.SecretCache;
import com.amazonaws.services.secretsmanager.AWSSecretsManager;
import com.amazonaws.services.secretsmanager.AWSSecretsManagerClientBuilder;
import com.amazonaws.services.secretsmanager.model.CreateSecretRequest;
import com.amazonaws.services.secretsmanager.model.DeleteSecretRequest;
import com.amazonaws.services.secretsmanager.model.ResourceNotFoundException;
import com.amazonaws.services.secretsmanager.model.UpdateSecretRequest;
import com.google.common.annotations.VisibleForTesting;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

/**
 * SecretPersistence implementation for AWS Secret Manager using <a href=
 * "https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/secretsmanager/package-summary.html">Java
 * SDK</a> The current implementation doesn't make use of `SecretCoordinate#getVersion` as this
 * version is non-compatible with how AWS secret manager deals with versions. In AWS versions is an
 * internal idiom that can is accessible, but it's a UUID + a tag <a href=
 * "https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/secretsmanager/SecretsManagerClient.html#listSecretVersionIds--">more
 * details.</a>
 */
@Slf4j
public class AWSSecretManagerPersistence implements SecretPersistence {

  private final AWSSecretsManager client;

  @VisibleForTesting
  protected final SecretCache cache;

  /**
   * Creates a AWSSecretManagerPersistence using the default client and region from the current AWS
   * credentials. Recommended way based on
   * <a href="https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html">this</a>
   * This implementation makes use of SecretCache as optimization to access secrets.
   *
   * @see SecretCache
   */
  public AWSSecretManagerPersistence() {
    this.client = AWSSecretsManagerClientBuilder.defaultClient();
    this.cache = new SecretCache(this.client);
  }

  /**
   * Creates a AWSSecretManagerPersistence overriding the current region. This implementation makes
   * use of SecretCache as optimization to access secrets
   *
   * @param region AWS region to use.
   * @see SecretCache
   */
  public AWSSecretManagerPersistence(final String region) {
    checkNotNull(region, "Region cannot be null, to use a default region call AWSSecretManagerPersistence.AWSSecretManagerPersistence()");
    checkArgument(!region.isEmpty(), "Region can't be empty, to use a default region call AWSSecretManagerPersistence.AWSSecretManagerPersistence()");
    this.client = AWSSecretsManagerClientBuilder
        .standard()
        .withRegion(region)
        .build();
    this.cache = new SecretCache(this.client);
  }

  /**
   * Creates a new AWSSecretManagerPersistence using the provided explicitly passed credentials.
   *
   * @param awsAccessKey The AWS access key.
   * @param awsSecretAccessKey The AWS secret access key.
   */
  public AWSSecretManagerPersistence(final String awsAccessKey, final String awsSecretAccessKey) {
    checkNotNull(awsAccessKey, "awsAccessKey cannot be null, to use a default region call AWSSecretManagerPersistence.AWSSecretManagerPersistence()");
    checkNotNull(awsSecretAccessKey,
        "awsSecretAccessKey cannot be null, to use a default region call AWSSecretManagerPersistence.AWSSecretManagerPersistence()");
    checkArgument(!awsAccessKey.isEmpty(),
        "awsAccessKey cannot be empty, to use a default region call AWSSecretManagerPersistence.AWSSecretManagerPersistence()");
    checkArgument(!awsSecretAccessKey.isEmpty(),
        "awsSecretAccessKey cannot be empty, to use a default region call AWSSecretManagerPersistence.AWSSecretManagerPersistence()");
    BasicAWSCredentials credentials = new BasicAWSCredentials(awsAccessKey, awsSecretAccessKey);
    this.client = AWSSecretsManagerClientBuilder
        .standard()
        .withCredentials(new AWSStaticCredentialsProvider(credentials))
        .build();
    this.cache = new SecretCache(this.client);
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    // fail fast, return an empty
    if (coordinate == null)
      return Optional.empty();

    String secretString = null;
    try {
      log.debug("Reading secret {}", coordinate.getCoordinateBase());
      secretString = cache.getSecretString(coordinate.getCoordinateBase());
    } catch (ResourceNotFoundException e) {
      log.warn("Secret {} not found", coordinate.getCoordinateBase());
    }
    return Optional.ofNullable(secretString);
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    checkNotNull(coordinate, "SecretCoordinate cannot be null");
    checkNotNull(payload, "Payload cannot be null");
    checkArgument(!payload.isEmpty(), "Payload shouldn't be empty");

    if (read(coordinate).isPresent()) {
      log.debug("Secret {} found updating payload.", coordinate.getCoordinateBase());
      final UpdateSecretRequest request = new UpdateSecretRequest()
          .withSecretId(coordinate.getCoordinateBase())
          .withSecretString(payload)
          .withDescription("Airbyte secret.");
      client.updateSecret(request);
    } else {
      log.debug("Secret {} not found, creating a new one.", coordinate.getCoordinateBase());
      final CreateSecretRequest secretRequest = new CreateSecretRequest()
          .withName(coordinate.getCoordinateBase())
          .withSecretString(payload)
          .withDescription("Airbyte secret.");
      client.createSecret(secretRequest);
    }

  }

  /**
   * Utility to clean up after integration tests.
   *
   * @param coordinate SecretCoordinate to delete.
   */
  @VisibleForTesting
  protected void deleteSecret(final SecretCoordinate coordinate) {
    client.deleteSecret(new DeleteSecretRequest()
        .withSecretId(coordinate.getCoordinateBase())
        .withForceDeleteWithoutRecovery(true));
  }

}
