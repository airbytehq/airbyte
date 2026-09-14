/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.bigquery

import com.google.cloud.bigquery.FieldList
import com.google.cloud.bigquery.FieldValueList

class BigQueryResultSet(val rowValues: FieldValueList, val fieldList: FieldList)
