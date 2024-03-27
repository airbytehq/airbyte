/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import org.apache.commons.lang3.function.FailableSupplier;

@FunctionalInterface
public interface CheckedSupplier<T, E extends Throwable> extends FailableSupplier<T, E> {

}
