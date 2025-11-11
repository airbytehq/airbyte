/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.lang

object MoreBooleans {
    /**
     * Safely handles converting boxed Booleans to booleans, even when they are null. Evaluates null
     * as false.
     *
     * @param bool boxed
     * @return unboxed
     */
    fun isTruthy(bool: Boolean?): Boolean {
        return bool != null && bool
    }
}
