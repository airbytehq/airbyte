package io.airbyte.cdk.load.file.s3

import kotlinx.coroutines.flow.flow
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.ListObjectsRequest
import com.amazonaws.services.s3.model.ObjectListing
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.object_storage.StateObjectStorageLite
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow

@Singleton
class S3ClientJavaSDK(
    private val s3Client: AmazonS3,
    private val bucketConfigProvider: S3BucketConfigurationProvider,
): StateObjectStorageLite<S3Object> {

    override fun list(prefix: String): Flow<S3Object> = flow {
        val bucket: String = bucketConfigProvider.s3BucketConfiguration.s3BucketName
        var objects: ObjectListing =
            s3Client.listObjects(
                ListObjectsRequest()
                    .withBucketName(bucket)
                    .withPrefix(prefix)
                    .withDelimiter("")
                    .withMaxKeys(1000)
            )

        // not sure why we would want to suspend here but keeping it for parity
        objects.objectSummaries.forEach {
            emit(S3Object(it.key!!, bucketConfigProvider.s3BucketConfiguration))
        }

        while (objects.objectSummaries.size > 0) {
            if (objects.isTruncated) {
                objects = s3Client.listNextBatchOfObjects(objects)
            } else {
                break
            }
        }
    }

    override fun getMetadata(key: String): Map<String, String> {
        val bucket: String = bucketConfigProvider.s3BucketConfiguration.s3BucketName
        val objectMetadata = s3Client.getObjectMetadata(bucket, key)
        return objectMetadata.userMetadata
    }
}
