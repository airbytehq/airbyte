/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

@FunctionalInterface
public interface CheckedFunction<T, R, E extends Throwable> {

  R apply(T t) throws E;

}
