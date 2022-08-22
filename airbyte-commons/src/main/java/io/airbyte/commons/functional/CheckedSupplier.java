/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

@FunctionalInterface
public interface CheckedSupplier<T, E extends Throwable> {

  T get() throws E;

}
