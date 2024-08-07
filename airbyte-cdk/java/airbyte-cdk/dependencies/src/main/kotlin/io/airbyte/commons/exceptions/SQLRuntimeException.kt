/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.exceptions

import java.sql.SQLException

/**
 * Wrapper unchecked exception for [SQLException]. This can be used in functional interfaces that do
 * not allow checked exceptions without the generic RuntimeException.
 */
class SQLRuntimeException(cause: SQLException?) : RuntimeException(cause)
