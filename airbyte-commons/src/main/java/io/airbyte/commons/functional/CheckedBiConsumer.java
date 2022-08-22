/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

@FunctionalInterface
public interface CheckedBiConsumer<T, R, E extends Throwable> {

  void accept(T t, R r) throws E;

}
