/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.NoCredentials
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
import java.io.ByteArrayInputStream
import org.apache.iceberg.gcp.GCPProperties
import org.apache.iceberg.gcp.auth.GoogleAuthManager
import org.apache.iceberg.gcp.gcs.GCSFileIO
import org.apache.iceberg.io.DelegateFileIO
import org.apache.iceberg.io.FileInfo
import org.apache.iceberg.io.InputFile
import org.apache.iceberg.io.OutputFile
import org.apache.iceberg.util.SerializableSupplier

class GcsDataLakeFileIO : DelegateFileIO {
    private lateinit var delegate: GCSFileIO

    override fun initialize(props: Map<String, String>) {
        if (::delegate.isInitialized) {
            delegate.close()
        }
        delegate =
            GCSFileIO(
                GcsStorageSupplier(
                    projectId = requireNotNull(props[GCPProperties.GCS_PROJECT_ID]),
                    serviceHost = props[GCPProperties.GCS_SERVICE_HOST],
                    noAuth = props[GCPProperties.GCS_NO_AUTH].toBoolean(),
                    credentialsJson = props[GoogleAuthManager.GCP_CREDENTIALS_JSON_PROPERTY],
                ),
            )
        delegate.initialize(props)
    }

    override fun newInputFile(path: String): InputFile = delegate.newInputFile(path)

    override fun newInputFile(path: String, length: Long): InputFile =
        delegate.newInputFile(path, length)

    override fun newOutputFile(path: String): OutputFile = delegate.newOutputFile(path)

    override fun deleteFile(path: String) = delegate.deleteFile(path)

    override fun listPrefix(prefix: String): Iterable<FileInfo> = delegate.listPrefix(prefix)

    override fun deletePrefix(prefix: String) = delegate.deletePrefix(prefix)

    override fun deleteFiles(paths: Iterable<String>) = delegate.deleteFiles(paths)

    override fun properties(): Map<String, String> = delegate.properties()

    override fun close() {
        if (::delegate.isInitialized) {
            delegate.close()
        }
    }

    fun client(): Storage = delegate.client()
}

class GcsStorageSupplier(
    private val projectId: String,
    private val serviceHost: String?,
    private val noAuth: Boolean,
    private val credentialsJson: String?,
) : SerializableSupplier<Storage> {
    override fun get(): Storage {
        val credentials =
            if (noAuth) {
                NoCredentials.getInstance()
            } else {
                val json =
                    credentialsJson?.takeIf(String::isNotBlank)
                        ?: throw IllegalStateException(
                            "Missing required property '${GoogleAuthManager.GCP_CREDENTIALS_JSON_PROPERTY}' when '${GCPProperties.GCS_NO_AUTH}' is false.",
                        )
                ByteArrayInputStream(json.toByteArray(Charsets.UTF_8)).use {
                    GoogleCredentials.fromStream(it)
                        .createScoped(listOf("https://www.googleapis.com/auth/cloud-platform"))
                }
            }

        val options =
            StorageOptions.newBuilder().setProjectId(projectId).setCredentials(credentials)
        serviceHost?.takeIf(String::isNotBlank)?.let(options::setHost)

        return options.build().service
    }
}
