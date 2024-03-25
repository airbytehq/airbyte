/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import org.apache.commons.lang3.function.FailableFunction;

@FunctionalInterface
public interface CheckedFunction<T, R, E extends Throwable> extends FailableFunction<T, R, E> {

}
