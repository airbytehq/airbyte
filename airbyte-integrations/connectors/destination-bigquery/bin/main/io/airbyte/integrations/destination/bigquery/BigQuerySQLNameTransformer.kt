/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.data.Transformations

/**
 * A legacy class. This used to inherit from the old CDK's StandardNameTransformer. You probably
 * should avoid adding new uses of this class.
 *
 * (I have no explanation for the method names.)
 */
class BigQuerySQLNameTransformer {
    /** This seemingly is what we use for any table/column name. */
    fun convertStreamName(input: String): String {
        val result = Transformations.toAlphanumericAndUnderscore(input)
        if (!result.substring(0, 1).matches("[A-Za-z_]".toRegex())) {
            // has to start with a letter or _
            return "_$result"
        }
        return result
    }

    /**
     * BigQuery allows a number to be the first character of a originalNamespace. Datasets that
     * begin with an underscore are hidden databases, and we cannot query
     * <hidden-dataset>.INFORMATION_SCHEMA. So we append a letter instead of underscore for
     * normalization. Reference: https://cloud.google.com/bigquery/docs/datasets#dataset-naming
     * </hidden-dataset>
     */
    fun getNamespace(namespace: String): String {
        val normalizedName = Transformations.toAlphanumericAndUnderscore(namespace)
        if (!normalizedName.substring(0, 1).matches("[A-Za-z0-9]".toRegex())) {
            return BigQueryConsts.NAMESPACE_PREFIX + normalizedName
        }
        return normalizedName
    }

    @Deprecated("")
    fun getTmpTableName(streamName: String, randomSuffix: String): String {
        return convertStreamName("_airbyte_tmp" + "_" + randomSuffix + "_" + streamName)
    }
}
