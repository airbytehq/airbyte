/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.azure.storage.blob.models.BlobRange;
import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;
import java.util.function.Consumer;

public abstract class AbstractGcsAzureUploader<T extends S3Writer> extends AbstractAzureUploader<S3Writer> {

    private static final Logger LOGGER = LoggerFactory.getLogger(AbstractGcsAzureUploader.class);

    private final boolean keepFilesInGcs;
    private final int headerByteSize;
    private final DestinationSyncMode syncMode;
    protected final AppendBlobClient appendBlobClient;
    protected final GcsDestinationConfig gcsDestinationConfig;

    AbstractGcsAzureUploader(
            DestinationSyncMode syncMode,
            T writer,
            GcsDestinationConfig gcsDestinationConfig,
            AppendBlobClient appendBlobClient,
            boolean keepFilesInGcs,
            int headerByteSize) {
        super(writer);
        this.syncMode = syncMode;
        this.keepFilesInGcs = keepFilesInGcs;
        this.headerByteSize = headerByteSize;
        this.appendBlobClient = appendBlobClient;
        this.gcsDestinationConfig = gcsDestinationConfig;
    }

    @Override
    public void postProcessAction(boolean hasFailed) throws Exception {
        if (!keepFilesInGcs) {
            deleteGcsFiles();
        }
    }

    @Override
    protected void uploadData(Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) throws Exception {
        uploadDataFromFileToTmpTable();
        super.uploadData(outputRecordCollector, lastStateMessage);
    }

    protected void uploadDataFromFileToTmpTable() throws Exception {
        final GcsDestinationConfig gcsDestinationConfig = this.gcsDestinationConfig;
        final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

        final String gcsBucketName = gcsDestinationConfig.getBucketName();
        long contentLength = s3Client.getObjectMetadata(gcsBucketName, this.writer.getOutputPath()).getContentLength();
        if (contentLength > 0) {
            LocalDateTime date = LocalDateTime.now().plusHours(25);
            Date out = Date.from(date.atZone(ZoneId.systemDefault()).toInstant());
            var url = s3Client.generatePresignedUrl(gcsBucketName, this.writer.getOutputPath(), out);
            appendBlobClient.appendBlockFromUrl(url.toString(), new BlobRange(headerByteSize));
        }
    }

    private void deleteGcsFiles() {
        final GcsDestinationConfig gcsDestinationConfig = this.gcsDestinationConfig;
        final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

        final String gcsBucketName = gcsDestinationConfig.getBucketName();
        final String gcs_bucket_path = gcsDestinationConfig.getBucketPath();

        final List<S3ObjectSummary> objects = s3Client
                .listObjects(gcsBucketName, gcs_bucket_path)
                .getObjectSummaries();

        objects.stream().filter(s3ObjectSummary -> s3ObjectSummary.getKey().equals(writer.getOutputPath())).forEach(s3ObjectSummary -> {
            s3Client.deleteObject(gcsBucketName, new DeleteObjectsRequest.KeyVersion(s3ObjectSummary.getKey()).getKey());
            LOGGER.info("File is deleted : " + s3ObjectSummary.getKey());
        });
        s3Client.shutdown();
    }

}
