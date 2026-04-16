/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.functional

import org.apache.commons.lang3.function.FailableConsumer

fun interface CheckedConsumer<T, E : Throwable?> : FailableConsumer<T, E>
