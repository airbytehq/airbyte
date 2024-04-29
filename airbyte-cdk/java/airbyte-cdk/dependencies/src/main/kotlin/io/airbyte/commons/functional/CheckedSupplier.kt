/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.functional

import org.apache.commons.lang3.function.FailableSupplier

fun interface CheckedSupplier<T, E : Throwable?> : FailableSupplier<T, E>
