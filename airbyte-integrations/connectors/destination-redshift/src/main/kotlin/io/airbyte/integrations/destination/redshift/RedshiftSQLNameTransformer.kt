/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.util.*

class RedshiftSQLNameTransformer : StandardNameTransformer() {
    override fun convertStreamName(input: String): String {
        return super.convertStreamName(input).lowercase(Locale.getDefault())
    }
}
