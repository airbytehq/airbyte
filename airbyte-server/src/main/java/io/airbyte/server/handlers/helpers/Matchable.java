/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers.helpers;

@FunctionalInterface
interface Matchable<K> {

  K match(K k);

}
