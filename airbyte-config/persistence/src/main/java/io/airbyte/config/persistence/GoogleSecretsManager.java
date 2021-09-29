/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.secretmanager.v1.AccessSecretVersionResponse;
import com.google.cloud.secretmanager.v1.ProjectName;
import com.google.cloud.secretmanager.v1.Replication;
import com.google.cloud.secretmanager.v1.Secret;
import com.google.cloud.secretmanager.v1.SecretManagerServiceClient;
import com.google.cloud.secretmanager.v1.SecretManagerServiceSettings;
import com.google.cloud.secretmanager.v1.SecretName;
import com.google.cloud.secretmanager.v1.SecretPayload;
import com.google.cloud.secretmanager.v1.SecretVersion;
import com.google.cloud.secretmanager.v1.SecretVersionName;
import com.google.common.base.Preconditions;
import com.google.protobuf.ByteString;
import io.airbyte.config.EnvConfigs;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Wrapper class to simplify the API for accessing secrets
 */
public class GoogleSecretsManager {

  /**
   * Manual test fixture to make sure you've got your project id set in env and have appropriate creds
   * to reach/write the secret store.
   */
  public static void main(String[] args) throws Exception {
    // Check that we're configured to a usable GCP project.
    EnvConfigs envConfig = new EnvConfigs();
    String projectId = envConfig.getSecretStoreGcpProjectId();
    Preconditions.checkNotNull(projectId, "Project ID must not be empty");
    Preconditions.checkNotNull(Long.parseLong(projectId), "Project ID must be purely numeric, not %s".format(projectId));

    // Check that we can read an existing one from that project / have permissions etc.
    Preconditions.checkArgument(existsSecret("zzzzzz") == false, "Secret doesn't exist, should return false.");
    Preconditions.checkArgument(existsSecret("dev_practice_sample_secret"), "Secret already exists, should return true.");
    String content = readSecret("dev_practice_sample_secret");
    Preconditions.checkArgument("ThisIsMyTest".equals(content));

    // Try creating a new one and reading it back.
    String rand = UUID.randomUUID().toString();
    String key = "dev_practice_sample_" + rand;
    saveSecret(key, rand);
    String rand2 = readSecret(key);
    Preconditions.checkArgument(rand.equals(rand2), "Values should have matched after writing and re-reading a new key.");
    saveSecret(key, "foo");
    deleteSecret(key);
  }

  public static String readSecret(String secretId) throws IOException {
    EnvConfigs envConfig = new EnvConfigs();
    String projectId = envConfig.getSecretStoreGcpProjectId();
    try (SecretManagerServiceClient client = getSecretManagerServiceClient()) {
      SecretVersionName secretVersionName = SecretVersionName.of(projectId, secretId, "latest");
      AccessSecretVersionResponse response = client.accessSecretVersion(secretVersionName);
      return response.getPayload().getData().toStringUtf8();
    } catch (com.google.api.gax.rpc.NotFoundException e) {
      return null;
    }
  }

  private static SecretManagerServiceClient getSecretManagerServiceClient() throws IOException {
    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream((new EnvConfigs()).getSecretStoreGcpCredentials().getBytes(StandardCharsets.UTF_8)));
    return SecretManagerServiceClient.create(
        SecretManagerServiceSettings.newBuilder().setCredentialsProvider(FixedCredentialsProvider.create(credentials)).build());
  }

  public static boolean existsSecret(String secretId) throws IOException {
    EnvConfigs envConfig = new EnvConfigs();
    String projectId = envConfig.getSecretStoreGcpProjectId();
    try (SecretManagerServiceClient client = getSecretManagerServiceClient()) {
      System.out.println("Project ID: " + projectId);
      System.out.println("Secret ID: " + secretId);
      SecretVersionName secretVersionName = SecretVersionName.of(projectId, secretId, "latest");
      System.out.println(secretVersionName);
      AccessSecretVersionResponse response = client.accessSecretVersion(secretVersionName);
      return true;
    } catch (com.google.api.gax.rpc.NotFoundException e) {
      return false;
    }
  }

  public static void saveSecret(String secretId, String value) throws IOException {
    EnvConfigs envConfig = new EnvConfigs();
    String projectId = envConfig.getSecretStoreGcpProjectId();
    try (SecretManagerServiceClient client = getSecretManagerServiceClient()) {
      if (!existsSecret(secretId)) {
        Secret secret = Secret.newBuilder().setReplication(Replication.newBuilder().setAutomatic(
            Replication.Automatic.newBuilder().build()).build()).build();
        Secret createdSecret = client.createSecret(ProjectName.of(projectId), secretId, secret);
      }
      SecretPayload payload = SecretPayload.newBuilder()
          .setData(ByteString.copyFromUtf8(value))
          .build();
      SecretVersion version = client.addSecretVersion(SecretName.of(projectId, secretId), payload);
    }
  }

  public static void deleteSecret(String secretId) throws IOException {
    EnvConfigs envConfig = new EnvConfigs();
    String projectId = envConfig.getSecretStoreGcpProjectId();
    try (SecretManagerServiceClient client = getSecretManagerServiceClient()) {
      SecretName secretName = SecretName.of(projectId, secretId);
      client.deleteSecret(secretName);
    }
  }

  public static List<String> listSecretsMatching(String prefix) throws IOException {
    final String PREFIX_REGEX = "projects/\\d+/secrets/";
    List<String> names = new ArrayList<String>();
    try (SecretManagerServiceClient client = getSecretManagerServiceClient()) {
      client.listSecrets(ProjectName.of(new EnvConfigs().getSecretStoreGcpProjectId())).iterateAll()
          .forEach(
              secret -> {
                if (secret.getName().replaceFirst(PREFIX_REGEX, "").startsWith(prefix)) {
                  names.add(secret.getName().replaceFirst(PREFIX_REGEX, ""));
                }
              });
    }
    return names;
  }

}
