/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

@FunctionalInterface
public interface CheckedConsumer<T, E extends Throwable> {

  void accept(T t) throws E;

}
