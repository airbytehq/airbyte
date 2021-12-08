/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import io.airbyte.config.storage.CloudStorageConfigs.MinioConfig;
import io.airbyte.config.storage.CloudStorageConfigs.S3Config;
import io.airbyte.config.storage.DefaultGcsClientFactory;
import io.airbyte.config.storage.DefaultS3ClientFactory;
import io.airbyte.config.storage.MinioS3ClientFactory;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;

/**
 * Leverages the CloudDocumentStore. The root directory is state and then each activityRunId is the
 * key.
 */
public class StateStore {

  private static final Path STATE_ROOT = Path.of("state");

  private final CloudDocumentStoreClient documentStoreClient;

  public StateStore s3(final S3Config config) {
    return new StateStore(new S3CloudDocumentStoreClient(
        new DefaultS3ClientFactory(config).get(),
        config.getBucketName(),
        STATE_ROOT));
  }

  public StateStore minio(final MinioConfig config) {
    return new StateStore(new S3CloudDocumentStoreClient(
        new MinioS3ClientFactory(config).get(),
        config.getBucketName(),
        STATE_ROOT));
  }

  public StateStore gcs(final GcsConfig config) {
    return new StateStore(new GcsCloudDocumentStoreClient(
        new DefaultGcsClientFactory(config).get(),
        config.getBucketName(),
        STATE_ROOT));
  }

  public StateStore dockerCompose(final Path workspaceMount) {
    return new StateStore(new DockerComposeDocumentStoreClient(workspaceMount));
  }

  public StateStore(final CloudDocumentStoreClient documentStoreClient) {
    this.documentStoreClient = documentStoreClient;
  }

  /**
   * Set the state for an activity run. Overwrites existing state if present.
   *
   * @param activityRunId - id to associate state with
   * @param state - state to persist
   */
  void setState(final UUID activityRunId, final State state) {
    documentStoreClient.write(activityRunId.toString(), Jsons.serialize(state));
  }

  /**
   * Fetch previously persisted state.
   *
   * @param activityRunId - id state is associated with
   * @return returns state if present, otherwise empty
   */
  Optional<State> getState(final UUID activityRunId) {
    return documentStoreClient.read(activityRunId.toString()).map(doc -> Jsons.deserialize(doc, State.class));
  }

  /**
   * Delete persisted state.
   *
   * @param activityRunId - id state is associated with
   * @return true if actually deletes something, otherwise false. (e.g. false if state doest not
   *         exist).
   */
  boolean deleteState(final UUID activityRunId) {
    return documentStoreClient.delete(activityRunId.toString());
  }

}
