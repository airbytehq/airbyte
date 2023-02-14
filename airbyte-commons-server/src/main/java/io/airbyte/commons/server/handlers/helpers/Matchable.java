/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers.helpers;

@FunctionalInterface
interface Matchable<K> {

  K match(K k);

}
