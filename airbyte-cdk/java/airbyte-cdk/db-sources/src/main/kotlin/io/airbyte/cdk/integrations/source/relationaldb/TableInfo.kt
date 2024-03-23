/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import lombok.Builder
import lombok.Getter

/**
 * This class encapsulates all externally relevant Table information.
 */
@Getter
@Builder
class TableInfo<T> {
    private val nameSpace: String? = null
    private val name: String? = null
    private val fields: List<T>? = null
    private val primaryKeys: List<String>? = null
    private val cursorFields: List<String>? = null
}
