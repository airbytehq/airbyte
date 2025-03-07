/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Dataset
import com.google.cloud.bigquery.DatasetInfo

object BigQueryUtils {
    fun getOrCreateDataset(
        bigquery: BigQuery,
        datasetId: String,
        datasetLocation: String,
    ): Dataset {
        var dataset = bigquery.getDataset(datasetId)
        if (dataset == null || !dataset.exists()) {
            val datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build()
            dataset = bigquery.create(datasetInfo)
        }
        return dataset
    }
}
