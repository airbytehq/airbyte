/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import java.util.Map;

/**
 * A custom stream transfer manager which overwrites the metadata on the
 * InitiateMultipartUploadRequest.
 * <p>
 * This is, apparently, the correct way to implement this functionality.
 * https://github.com/alexmojaki/s3-stream-upload/issues/3
 */
public class StreamTransferManagerWithMetadata extends StreamTransferManager {

  private final Map<String, String> userMetadata;

  public StreamTransferManagerWithMetadata(final String bucketName,
                                           final String putKey,
                                           final AmazonS3 s3Client,
                                           final Map<String, String> userMetadata) {
    super(bucketName, putKey, s3Client);
    this.userMetadata = userMetadata;
  }

  @Override
  public void customiseInitiateRequest(final InitiateMultipartUploadRequest request) {
    if (userMetadata != null) {
      ObjectMetadata objectMetadata = request.getObjectMetadata();
      if (objectMetadata == null) {
        objectMetadata = new ObjectMetadata();
      }
      objectMetadata.setUserMetadata(userMetadata);
      request.setObjectMetadata(objectMetadata);
    }
  }

}
