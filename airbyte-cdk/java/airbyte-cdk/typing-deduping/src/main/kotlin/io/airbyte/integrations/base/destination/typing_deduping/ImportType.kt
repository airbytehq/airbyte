/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping

enum class ImportType {
    APPEND,
    DEDUPE,
}
