/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

/**
 * Represents the mathematical concept of partial ordering. Unlike Comparable, the compareTo method
 * can return null when the two elements don't have a natural ordering.
 *
 * We use this interface to compare CDC positions to see when we have reached the target offset or
 * to determine whether we are still making progress. We need partial ordering rather than a full
 * ordering like Comparable because sometimes we are missing some fields in the offset and can't
 * determine whether one offset is beyond another. In these cases, we typically continue until we
 * encounter a fully populated offset.
 *
 * The supplied convenience methods handle the null checking and allow us to make these kinds of
 * comparisons ergonomically.
 */
fun interface PartiallyOrdered<T> {
    fun compareTo(other: T): Int?
}

// Convenience methods
fun <T : PartiallyOrdered<T>> T?.isGreater(other: T?): Boolean {
    if (this == null || other == null) return false
    val comparison = this.compareTo(other)
    return comparison != null && comparison > 0
}

fun <T : PartiallyOrdered<T>> T?.isGreaterOrEqual(other: T?): Boolean {
    if (this == null || other == null) return false
    val comparison = this.compareTo(other)
    return comparison != null && comparison >= 0
}
