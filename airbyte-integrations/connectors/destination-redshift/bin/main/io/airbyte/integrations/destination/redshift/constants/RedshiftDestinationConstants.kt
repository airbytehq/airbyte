/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.constants

import org.jooq.DataType
import org.jooq.impl.DefaultDataType

/** Constant holder for Redshift Destination */
object RedshiftDestinationConstants {
    const val UPLOADING_METHOD: String = "uploading_method"

    val SUPER_TYPE: DataType<String?> = DefaultDataType(null, String::class.java, "super")

    const val DROP_CASCADE_OPTION: String = "drop_cascade"
}
