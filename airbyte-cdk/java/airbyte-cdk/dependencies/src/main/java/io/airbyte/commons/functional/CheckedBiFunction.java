/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import org.apache.commons.lang3.function.FailableBiFunction;

public interface CheckedBiFunction<First, Second, Result, E extends Throwable> extends FailableBiFunction<First, Second, Result, E> {

}
