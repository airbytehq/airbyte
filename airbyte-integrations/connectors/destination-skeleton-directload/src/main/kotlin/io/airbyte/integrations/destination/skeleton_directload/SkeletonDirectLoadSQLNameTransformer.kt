/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.skeleton_directload

import io.airbyte.cdk.load.data.Transformations

class SkeletonDirectLoadSQLNameTransformer {
    fun convertStreamName(input: String): String {
        val result = Transformations.toAlphanumericAndUnderscore(input)
        return result
    }

    fun getNamespace(namespace: String): String {
        val normalizedName = Transformations.toAlphanumericAndUnderscore(namespace)
        return normalizedName
    }

    @Deprecated("")
    fun getTmpTableName(streamName: String, randomSuffix: String): String {
        return convertStreamName("_airbyte_tmp" + "_" + randomSuffix + "_" + streamName)
    }
}
