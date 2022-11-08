/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.api.gax.rpc.NotFoundException;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.secretmanager.v1.ProjectName;
import com.google.cloud.secretmanager.v1.Replication;
import com.google.cloud.secretmanager.v1.Secret;
import com.google.cloud.secretmanager.v1.SecretManagerServiceClient;
import com.google.cloud.secretmanager.v1.SecretManagerServiceSettings;
import com.google.cloud.secretmanager.v1.SecretName;
import com.google.cloud.secretmanager.v1.SecretPayload;
import com.google.cloud.secretmanager.v1.SecretVersionName;
import com.google.protobuf.ByteString;
import com.google.protobuf.Duration;
import io.airbyte.commons.lang.Exceptions;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import org.joda.time.Days;

/**
 * Uses Google Secret Manager (https://cloud.google.com/secret-manager) as a K/V store to access
 * secrets. In the future we will likely want to introduce more granular permission handling here.
 *
 * It's important to note that we are not making use of the versioning feature of Google Secret
 * Manager. This is for a few reasons: 1. There isn't a clean interface for getting the most recent
 * version. 2. Version writes must be sequential. This means that if we wanted to move between
 * secrets management platforms such as Hashicorp Vault and GSM, we would need to create secrets in
 * order (or depending on our retention for the secrets pretend to insert earlier versions).
 */
final public class GoogleSecretManagerPersistence implements SecretPersistence {

  /**
   * The "latest" alias is a magic string that gives you access to the latest secret without
   * explicitly specifying the version. For more info see:
   * https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#access
   */
  private static final String LATEST = "latest";

  private static final Duration EPHEMERAL_TTL = Duration.newBuilder()
      .setSeconds(Days.days(5).toStandardSeconds().getSeconds())
      .build();

  private static final Replication REPLICATION_POLICY = Replication.newBuilder()
      .setAutomatic(Replication.Automatic.newBuilder().build())
      .build();

  private final String gcpProjectId;
  private final Supplier<SecretManagerServiceClient> clientSupplier;

  private final @Nullable Duration ttl;

  /**
   * Creates a persistence with an infinite TTL for stored secrets. Used for source/destination config
   * secret storage.
   */
  public static GoogleSecretManagerPersistence getLongLived(final String gcpProjectId, final String gcpCredentialsJson) {
    return new GoogleSecretManagerPersistence(gcpProjectId, gcpCredentialsJson, null);
  }

  /**
   * Creates a persistence with a relatively short TTL for stored secrets. Used for temporary
   * operations such as check/discover operations where we need to use secret storage to communicate
   * from the server to Temporal, but where we don't want to maintain the secrets indefinitely.
   */
  public static GoogleSecretManagerPersistence getEphemeral(final String gcpProjectId, final String gcpCredentialsJson) {
    return new GoogleSecretManagerPersistence(gcpProjectId, gcpCredentialsJson, EPHEMERAL_TTL);
  }

  private GoogleSecretManagerPersistence(final String gcpProjectId, final String gcpCredentialsJson, final @Nullable Duration ttl) {
    this.gcpProjectId = gcpProjectId;
    this.clientSupplier = () -> Exceptions.toRuntime(() -> getSecretManagerServiceClient(gcpCredentialsJson));
    this.ttl = ttl;
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try (final var client = clientSupplier.get()) {
      final var secretVersionName = SecretVersionName.of(gcpProjectId, coordinate.getFullCoordinate(), LATEST);
      final var response = client.accessSecretVersion(secretVersionName);
      return Optional.of(response.getPayload().getData().toStringUtf8());
    } catch (final NotFoundException e) {
      return Optional.empty();
    }
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    try (final var client = clientSupplier.get()) {
      if (read(coordinate).isEmpty()) {
        final var secretBuilder = Secret.newBuilder().setReplication(REPLICATION_POLICY);

        if (ttl != null) {
          secretBuilder.setTtl(ttl);
        }

        client.createSecret(ProjectName.of(gcpProjectId), coordinate.getFullCoordinate(), secretBuilder.build());
      }

      final var name = SecretName.of(gcpProjectId, coordinate.getFullCoordinate());
      final var secretPayload = SecretPayload.newBuilder()
          .setData(ByteString.copyFromUtf8(payload))
          .build();

      client.addSecretVersion(name, secretPayload);
    }
  }

  public static SecretManagerServiceClient getSecretManagerServiceClient(final String credentialsJson) throws IOException {
    final var credentialsByteStream = new ByteArrayInputStream(credentialsJson.getBytes(StandardCharsets.UTF_8));
    final var credentials = ServiceAccountCredentials.fromStream(credentialsByteStream);
    final var clientSettings = SecretManagerServiceSettings.newBuilder()
        .setCredentialsProvider(FixedCredentialsProvider.create(credentials))
        .build();

    return SecretManagerServiceClient.create(clientSettings);
  }

}
