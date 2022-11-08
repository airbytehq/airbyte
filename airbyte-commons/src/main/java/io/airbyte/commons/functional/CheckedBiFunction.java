/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

public interface CheckedBiFunction<First, Second, Result, E extends Throwable> {

  Result apply(First first, Second second) throws E;

}
