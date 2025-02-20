/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.model

import com.fasterxml.jackson.annotation.JsonProperty

class AirbyteRecordMessageFile {
    constructor(
        fileUrl: String? = null,
        bytes: Long? = null,
        fileRelativePath: String? = null,
        modified: Long? = null,
        sourceFileUrl: String? = null
    ) {
        this.fileUrl = fileUrl
        this.bytes = bytes
        this.fileRelativePath = fileRelativePath
        this.modified = modified
        this.sourceFileUrl = sourceFileUrl
    }
    constructor() :
        this(
            fileUrl = null,
            bytes = null,
            fileRelativePath = null,
            modified = null,
            sourceFileUrl = null
        )

    @get:JsonProperty("file_url")
    @set:JsonProperty("file_url")
    @JsonProperty("file_url")
    var fileUrl: String? = null

    @get:JsonProperty("bytes")
    @set:JsonProperty("bytes")
    @JsonProperty("bytes")
    var bytes: Long? = null

    @get:JsonProperty("file_relative_path")
    @set:JsonProperty("file_relative_path")
    @JsonProperty("file_relative_path")
    var fileRelativePath: String? = null

    @get:JsonProperty("modified")
    @set:JsonProperty("modified")
    @JsonProperty("modified")
    var modified: Long? = null

    @get:JsonProperty("source_file_url")
    @set:JsonProperty("source_file_url")
    @JsonProperty("source_file_url")
    var sourceFileUrl: String? = null
}
