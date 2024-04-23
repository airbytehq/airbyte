/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.template

import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import java.sql.Timestamp
import java.util.Objects

/**
 * This class is used as argument holder S3FilenameTemplateManager.class
 *
 * @see S3FilenameTemplateManager.applyPatternToFilename
 */
class S3FilenameTemplateParameterObject
internal constructor(
    val objectPath: String?,
    private val recordsData: SerializableBuffer?,
    val fileNamePattern: String?,
    val fileExtension: String?,
    val partId: String?,
    val fileUploadFormat: FileUploadFormat?,
    val timestamp: Timestamp?,
    val customSuffix: String?
) {
    class S3FilenameTemplateParameterObjectBuilder internal constructor() {
        private var objectPath: String? = null
        private var recordsData: SerializableBuffer? = null
        private var fileNamePattern: String? = null
        private var fileExtension: String? = null
        private var partId: String? = null
        private var fileUploadFormat: FileUploadFormat? = null
        private var timestamp: Timestamp? = null
        private var customSuffix: String? = null

        fun objectPath(objectPath: String?): S3FilenameTemplateParameterObjectBuilder {
            this.objectPath = objectPath
            return this
        }

        fun recordsData(
            recordsData: SerializableBuffer?
        ): S3FilenameTemplateParameterObjectBuilder {
            this.recordsData = recordsData
            return this
        }

        fun fileNamePattern(fileNamePattern: String?): S3FilenameTemplateParameterObjectBuilder {
            this.fileNamePattern = fileNamePattern
            return this
        }

        fun fileExtension(fileExtension: String?): S3FilenameTemplateParameterObjectBuilder {
            this.fileExtension = fileExtension
            return this
        }

        fun partId(partId: String?): S3FilenameTemplateParameterObjectBuilder {
            this.partId = partId
            return this
        }

        fun s3Format(
            fileUploadFormat: FileUploadFormat?
        ): S3FilenameTemplateParameterObjectBuilder {
            this.fileUploadFormat = fileUploadFormat
            return this
        }

        fun timestamp(timestamp: Timestamp?): S3FilenameTemplateParameterObjectBuilder {
            this.timestamp = timestamp
            return this
        }

        fun customSuffix(customSuffix: String?): S3FilenameTemplateParameterObjectBuilder {
            this.customSuffix = customSuffix
            return this
        }

        fun build(): S3FilenameTemplateParameterObject {
            return S3FilenameTemplateParameterObject(
                objectPath,
                recordsData,
                fileNamePattern,
                fileExtension,
                partId,
                fileUploadFormat,
                timestamp,
                customSuffix,
            )
        }

        override fun toString(): String {
            return ("S3FilenameTemplateParameterObject.S3FilenameTemplateParameterObjectBuilder(objectPath=" +
                this.objectPath +
                ", recordsData=" +
                this.recordsData +
                ", fileNamePattern=" +
                this.fileNamePattern +
                ", fileExtension=" +
                this.fileExtension +
                ", partId=" +
                this.partId +
                ", s3Format=" +
                this.fileUploadFormat +
                ", timestamp=" +
                this.timestamp +
                ", customSuffix=" +
                this.customSuffix +
                ")")
        }
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as S3FilenameTemplateParameterObject
        return objectPath == that.objectPath &&
            recordsData == that.recordsData &&
            fileNamePattern == that.fileNamePattern &&
            fileExtension == that.fileExtension &&
            partId == that.partId &&
            fileUploadFormat == that.fileUploadFormat &&
            timestamp == that.timestamp &&
            customSuffix == that.customSuffix
    }

    override fun hashCode(): Int {
        return Objects.hash(
            objectPath,
            recordsData,
            fileNamePattern,
            fileExtension,
            partId,
            fileUploadFormat,
            timestamp,
            customSuffix,
        )
    }

    companion object {
        @JvmStatic
        fun builder(): S3FilenameTemplateParameterObjectBuilder {
            return S3FilenameTemplateParameterObjectBuilder()
        }
    }
}
