/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import com.google.cloud.storage.Blob;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import io.airbyte.config.storage.DefaultGcsClientFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Optional;

/**
 * Document store on top of the GCS Client (Storage).
 */
public class GcsDocumentStoreClient implements DocumentStoreClient {

  private final String bucketName;
  private final Path root;
  private final Storage gcsClient;

  public static GcsDocumentStoreClient create(final GcsConfig config, final Path root) {
    return new GcsDocumentStoreClient(
        new DefaultGcsClientFactory(config).get(),
        config.getBucketName(),
        root);
  }

  public GcsDocumentStoreClient(final Storage gcsClient, final String bucketName, final Path root) {
    this.gcsClient = gcsClient;
    this.bucketName = bucketName;
    this.root = root;
  }

  String getKey(final String id) {
    return root + "/" + id;
  }

  BlobId getBlobId(final String id) {
    return BlobId.of(bucketName, getKey(id));
  }

  @Override
  public void write(final String id, final String document) {
    final BlobInfo blobInfo = BlobInfo.newBuilder(getBlobId(id)).build();
    gcsClient.create(blobInfo, document.getBytes(StandardCharsets.UTF_8));
  }

  @Override
  public Optional<String> read(final String id) {
    final Blob blob = gcsClient.get(getBlobId(id));
    if (blob != null && blob.exists()) {
      return Optional.of(new String(gcsClient.readAllBytes(BlobId.of(bucketName, getKey(id))), StandardCharsets.UTF_8));
    } else {
      return Optional.empty();
    }
  }

  @Override
  public boolean delete(final String id) {
    return gcsClient.delete(BlobId.of(bucketName, getKey(id)));
  }

}
