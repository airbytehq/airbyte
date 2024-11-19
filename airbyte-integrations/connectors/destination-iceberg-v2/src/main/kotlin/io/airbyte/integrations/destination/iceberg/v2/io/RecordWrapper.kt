/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2.io

import org.apache.iceberg.data.Record
import org.apache.iceberg.types.Types

/**
 * Wraps the Iceberg [Record] class to add the potential delta [Operation] associated with the
 * record. All record operations are delegated to the provided [Record] object.
 */
data class RecordWrapper(val delegate: Record, val operation: Operation) : Record {
    override fun size(): Int {
        return delegate.size()
    }

    override fun get(pos: Int): Any {
        return delegate.get(pos)
    }

    override fun <T : Any?> get(pos: Int, javaClass: Class<T>?): T {
        return delegate.get(pos, javaClass)
    }

    override fun <T : Any?> set(pos: Int, value: T) {
        delegate.set(pos, value)
    }

    override fun struct(): Types.StructType {
        return delegate.struct()
    }

    override fun getField(name: String?): Any {
        return delegate.getField(name)
    }

    override fun setField(name: String?, value: Any?) {
        delegate.setField(name, value)
    }

    override fun copy(): Record {
        return delegate.copy()
    }

    override fun copy(overwriteValues: MutableMap<String, Any>?): Record {
        return delegate.copy(overwriteValues)
    }
}
