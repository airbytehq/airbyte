/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest
import com.amazonaws.services.s3.model.ObjectMetadata

/**
 * A custom stream transfer manager which overwrites the metadata on the
 * InitiateMultipartUploadRequest.
 *
 * This is, apparently, the correct way to implement this functionality.
 * https://github.com/alexmojaki/s3-stream-upload/issues/3
 */
class StreamTransferManagerWithMetadata(
    bucketName: String?,
    putKey: String?,
    s3Client: AmazonS3?,
    private val userMetadata: Map<String, String>?
) : StreamTransferManager(bucketName, putKey, s3Client) {
    override fun customiseInitiateRequest(request: InitiateMultipartUploadRequest) {
        if (userMetadata != null) {
            var objectMetadata = request.getObjectMetadata()
            if (objectMetadata == null) {
                objectMetadata = ObjectMetadata()
            }
            objectMetadata.userMetadata = userMetadata
            request.setObjectMetadata(objectMetadata)
        }
    }
}
