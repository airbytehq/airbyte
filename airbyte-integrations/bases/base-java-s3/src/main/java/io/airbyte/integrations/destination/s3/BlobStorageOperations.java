/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.joda.time.DateTime;

public abstract class BlobStorageOperations {

  protected final List<BlobDecorator> blobDecorators;

  protected BlobStorageOperations() {
    this.blobDecorators = new ArrayList<>();
  }

  public abstract String getBucketObjectPath(String namespace, String streamName, DateTime writeDatetime, String customFormat);

  /**
   * Ensure that the bucket specified in the config exists
   */
  public abstract void createBucketIfNotExists() throws Exception;

  /**
   * Upload the data files into the storage area.
   *
   * @return the name of the file that was uploaded.
   */
  public abstract String uploadRecordsToBucket(SerializableBuffer recordsData, String namespace, String streamName, String objectPath)
      throws Exception;

  /**
   * Remove files that were just stored in the bucket
   */
  public abstract void cleanUpBucketObject(String objectPath, List<String> stagedFiles) throws Exception;

  /**
   * Deletes all the bucket objects for the specified bucket path
   *
   * @param namespace Optional source-defined namespace name
   * @param streamName Name of the stream
   * @param objectPath file path to where staging files are stored
   * @param pathFormat formatted string for the path
   */
  public abstract void cleanUpBucketObject(String namespace, String streamName, String objectPath, String pathFormat);

  public abstract void dropBucketObject(String objectPath);

  public abstract boolean isValidData(JsonNode jsonNode);

  protected abstract Map<String, String> getMetadataMapping();

  public void addBlobDecorator(final BlobDecorator blobDecorator) {
    blobDecorators.add(blobDecorator);
  }

}
