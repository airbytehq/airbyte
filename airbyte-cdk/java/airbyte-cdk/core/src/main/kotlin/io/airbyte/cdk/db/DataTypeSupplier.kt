/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import java.sql.SQLException

fun interface DataTypeSupplier<DataType> {
    @Throws(SQLException::class) fun apply(): DataType
}
