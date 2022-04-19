/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import java.util.List;
import org.joda.time.DateTime;

public interface BlobStorageOperations {

  String getBucketObjectPath(String namespace, String streamName, DateTime writeDatetime, String customFormat);

  /**
   * Create a storage object where to store data in the destination for a @param objectPath
   */
  void createBucketObjectIfNotExists(String objectPath) throws Exception;

  /**
   * Upload the data files into the storage area.
   *
   * @return the name of the file that was uploaded.
   */
  String uploadRecordsToBucket(SerializableBuffer recordsData, String namespace, String streamName, String objectPath) throws Exception;

  /**
   * Remove files that were just stored in the bucket
   */
  void cleanUpBucketObject(String objectPath, List<String> stagedFiles) throws Exception;

  void cleanUpBucketObject(String namespace, String StreamName, String objectPath, String pathFormat);

  void dropBucketObject(String objectPath);

  boolean isValidData(JsonNode jsonNode);

}
