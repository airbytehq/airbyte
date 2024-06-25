/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

class UnexpectedSchemaException(message: String?) : RuntimeException(message)
