/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.functional

import org.apache.commons.lang3.function.FailableBiFunction

fun interface CheckedBiFunction<First, Second, Result, E : Throwable?> :
    FailableBiFunction<First, Second, Result, E>
