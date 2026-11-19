/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.google.cloud.storage.StorageException
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.gcs.GcsWorkloadIdentityFederationConfiguration
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClientFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.nio.file.Paths
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

/**
 * Connection checker: uploads a small probe file via [GcsClientFactory], verifies it can be listed,
 * then deletes it. Builds the client from the config directly (not via DI) per the
 * [DestinationChecker] contract.
 */
@Singleton
class GcsV2Checker<T : OutputStream>(
    private val timeProvider: TimeProvider,
) : DestinationChecker<GcsV2Configuration<T>> {
    private val log = KotlinLogging.logger {}

    override fun check(config: GcsV2Configuration<T>) {
        runBlocking {
            val gcsClient = GcsClientFactory.make(config.gcsClientConfiguration)
            val pathFactory = ObjectStoragePathFactory.from(config, timeProvider)
            val path = pathFactory.getFinalDirectory(mockStream())
            val key = Paths.get(path, "_EXAMPLE").toString()
            log.info { "Checking if destination can write to $path" }
            var gcsObject: GcsBlob? = null
            val compressor = config.objectStorageCompressionConfiguration.compressor
            try {
                val upload = gcsClient.startStreamingUpload(key)
                val byteStream = ByteArrayOutputStream()
                compressor.wrapper(byteStream).use { it.write("""{"data": 1}""") }
                upload.uploadPart(byteStream.toByteArray(), 1)
                gcsObject = upload.complete()
                val results = gcsClient.list(path).toList()
                if (results.isEmpty() || results.find { it.key == key } == null) {
                    throw IllegalStateException("Failed to write to GCS bucket")
                }
                log.info { "Successfully wrote test file: $results" }
            } catch (e: ConfigErrorException) {
                throw e
            } catch (e: Exception) {
                throw ConfigErrorException(describeFailure(config, e), e)
            } finally {
                gcsObject?.also {
                    gcsClient.delete(it)
                    log.info { "Successfully removed test file" }
                }
            }
        }
    }

    private fun describeFailure(config: GcsV2Configuration<T>, e: Exception): String {
        val bucket = config.gcsClientConfiguration.gcsBucketName
        val hint =
            when (config.gcsClientConfiguration.credential) {
                is GcsHmacKeyConfiguration -> hmacHint(bucket, e)
                is GcsWorkloadIdentityFederationConfiguration -> wifHint(bucket, e)
            }
        return "Could not write a test object to GCS bucket '$bucket'. $hint (underlying error: " +
            "${e.message ?: e::class.simpleName})"
    }

    internal companion object {
        /**
         * HMAC keys go through GCS's S3-compatible XML API, so SDK errors arrive in S3 terminology
         * (`AccessDenied`, `SignatureDoesNotMatch`, `NoSuchBucket`).
         */
        fun hmacHint(bucket: String, e: Exception): String {
            val cause = e.toString()
            return when {
                "SignatureDoesNotMatch" in cause || "InvalidAccessKeyId" in cause ->
                    "The HMAC key access ID or secret is wrong. Create a new HMAC key for the " +
                        "service account in Cloud Storage > Settings > Interoperability and " +
                        "paste both values without surrounding whitespace."
                "NoSuchBucket" in cause ->
                    "Bucket '$bucket' does not exist or the name is misspelled."
                "AccessDenied" in cause || "Forbidden" in cause || "403" in cause ->
                    "The HMAC key's service account lacks permissions on bucket '$bucket'. It " +
                        "needs storage.objects.create, storage.objects.list, " +
                        "storage.objects.delete, storage.objects.get and " +
                        "storage.multipartUploads.create/abort/list/listParts (for example the " +
                        "Storage Object Admin role on the bucket)."
                else -> "Verify the bucket name, region and HMAC key."
            }
        }

        /**
         * Workload Identity Federation goes through the GCS JSON API, so errors are
         * [StorageException]s carrying the HTTP status. A failed token exchange surfaces as an
         * `IOException` from the auth library, which the storage client wraps in a
         * [StorageException] without an HTTP status.
         */
        fun wifHint(bucket: String, e: Exception): String {
            val storageError =
                generateSequence<Throwable>(e) { it.cause }
                    .filterIsInstance<StorageException>()
                    .firstOrNull()
            return when (storageError?.code) {
                404 -> "Bucket '$bucket' does not exist or the name is misspelled."
                403 ->
                    "The federated identity lacks permissions on bucket '$bucket'. Grant the " +
                        "federated principal (or the service account it impersonates) the " +
                        "Storage Object User role (roles/storage.objectUser) on the bucket."
                401 ->
                    "Google rejected the federated credentials. Check that the credential " +
                        "configuration's audience matches the Workload Identity Pool provider."
                else ->
                    "Could not obtain a federated token. Check that the credential " +
                        "configuration's credential_source is readable from the connector, and " +
                        "that its audience matches the Workload Identity Pool provider and the " +
                        "provider accepts the subject token."
            }
        }
    }
}
