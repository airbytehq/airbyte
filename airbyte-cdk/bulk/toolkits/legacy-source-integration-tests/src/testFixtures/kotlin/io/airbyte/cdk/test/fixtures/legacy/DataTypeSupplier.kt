/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.sql.SQLException

fun interface DataTypeSupplier<DataType> {
    @Throws(SQLException::class) fun apply(): DataType
}
