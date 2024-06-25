/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/**
 * Exception thrown when a destination's v2 sync is attempting to write to a table which does not
 * have the expected columns used by airbyte.
 */
class TableNotMigratedException : RuntimeException {
    constructor(message: String?) : super(message)

    constructor(message: String?, cause: Throwable?) : super(message, cause)
}
