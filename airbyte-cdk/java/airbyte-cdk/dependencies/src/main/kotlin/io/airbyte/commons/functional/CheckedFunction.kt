/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.functional

import org.apache.commons.lang3.function.FailableFunction

fun interface CheckedFunction<T, R, E : Throwable?> : FailableFunction<T, R, E>
