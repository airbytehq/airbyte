package io.airbyte.cdk.read.cdc

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
