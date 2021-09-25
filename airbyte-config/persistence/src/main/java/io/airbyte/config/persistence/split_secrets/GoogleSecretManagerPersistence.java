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

package io.airbyte.config.persistence.split_secrets;

import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.api.gax.rpc.NotFoundException;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.secretmanager.v1.Replication;
import com.google.cloud.secretmanager.v1.Secret;
import com.google.cloud.secretmanager.v1.SecretManagerServiceClient;
import com.google.cloud.secretmanager.v1.SecretManagerServiceSettings;
import com.google.cloud.secretmanager.v1.SecretName;
import com.google.cloud.secretmanager.v1.SecretPayload;
import com.google.cloud.secretmanager.v1.SecretVersionName;
import com.google.protobuf.ByteString;
import io.airbyte.commons.lang.Exceptions;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.function.Supplier;

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
public class GoogleSecretManagerPersistence implements SecretPersistence {

  /**
   * The "latest" alias is a magic string that gives you access to the latest secret without
   * explicitly specifying the version. For more info see:
   * https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#access
   */
  private static final String LATEST = "latest";

  private final String gcpProjectId;
  private final Supplier<SecretManagerServiceClient> clientSupplier;

  public GoogleSecretManagerPersistence(final String gcpProjectId, final String gcpCredentialsJson) {
    this.gcpProjectId = gcpProjectId;
    this.clientSupplier = () -> Exceptions.toRuntime(() -> getSecretManagerServiceClient(gcpCredentialsJson));
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    try (final var client = clientSupplier.get()) {
      final var secretVersionName = SecretVersionName.of(gcpProjectId, coordinate.getFullCoordinate(), LATEST);
      final var response = client.accessSecretVersion(secretVersionName);
      return Optional.of(response.getPayload().getData().toStringUtf8());
    } catch (NotFoundException e) {
      return Optional.empty();
    }
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    try (final var client = clientSupplier.get()) {
      if (read(coordinate).isEmpty()) {
        final var replicationPolicy = Replication.newBuilder()
            .setAutomatic(Replication.Automatic.newBuilder().build())
            .build();

        final var secretConfiguration = Secret.newBuilder()
            .setReplication(replicationPolicy)
            .build();

        client.createSecret(gcpProjectId, coordinate.getFullCoordinate(), secretConfiguration);
      }

      final var name = SecretName.of(gcpProjectId, coordinate.getFullCoordinate());
      final var secretPayload = SecretPayload.newBuilder()
          .setData(ByteString.copyFromUtf8(payload))
          .build();

      client.addSecretVersion(name, secretPayload);
    }
  }

  public static SecretManagerServiceClient getSecretManagerServiceClient(String credentialsJson) throws IOException {
    final var credentialsByteStream = new ByteArrayInputStream(credentialsJson.getBytes(StandardCharsets.UTF_8));
    final var credentials = ServiceAccountCredentials.fromStream(credentialsByteStream);
    final var clientSettings = SecretManagerServiceSettings.newBuilder()
        .setCredentialsProvider(FixedCredentialsProvider.create(credentials))
        .build();

    return SecretManagerServiceClient.create(clientSettings);
  }

}
