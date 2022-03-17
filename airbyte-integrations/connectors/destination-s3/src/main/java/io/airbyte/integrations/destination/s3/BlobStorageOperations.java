/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.record_buffer.RecordBufferImplementation;
import java.util.List;
import org.joda.time.DateTime;

public interface BlobStorageOperations {

  String getBucketName(String namespace, String bucketName);

  String getBucketPath(String namespace, String bucketName, DateTime writeDatetime);

  /**
   * Create a storage bucket where to store data in the destination
   */
  void createBucketObjectIfNotExists(String bucketName) throws Exception;

  /**
   * Upload the data files into the storage area.
   *
   * @return the name of the file that was uploaded.
   */
  String uploadRecordsToBucket(RecordBufferImplementation recordsData, String namespace, String bucketPath) throws Exception;

  /**
   * Remove files that were just stored in the bucket
   */
  void cleanUpBucketObjects(String bucketPath, List<String> stagedFiles) throws Exception;

  void dropBucketObject(String stageName);

  boolean isValidData(JsonNode jsonNode);

}
