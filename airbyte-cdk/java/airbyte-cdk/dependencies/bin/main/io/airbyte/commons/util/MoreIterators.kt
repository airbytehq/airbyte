/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import com.google.common.collect.AbstractIterator
import java.util.*
import java.util.function.Supplier

object MoreIterators {
    /**
     * Create an iterator from elements
     *
     * @param elements element to put in iterator
     * @param <T> type
     * @return iterator with all elements </T>
     */
    @SafeVarargs
    @JvmStatic
    fun <T> of(vararg elements: T): Iterator<T> {
        return Arrays.asList(*elements).iterator()
    }

    /**
     * Create a list from an iterator
     *
     * @param iterator iterator to convert
     * @param <T> type
     * @return list </T>
     */
    @JvmStatic
    fun <T> toList(iterator: Iterator<T>): List<T> {
        val list: MutableList<T> = ArrayList()
        while (iterator.hasNext()) {
            list.add(iterator.next())
        }
        return list
    }

    /**
     * Create a set from an iterator
     *
     * @param iterator iterator to convert
     * @param <T> type
     * @return set </T>
     */
    @JvmStatic
    fun <T> toSet(iterator: Iterator<T>): Set<T> {
        val set: MutableSet<T> = HashSet()
        while (iterator.hasNext()) {
            set.add(iterator.next())
        }
        return set
    }

    @JvmStatic
    fun <T> singletonIteratorFromSupplier(supplier: Supplier<T>): Iterator<T> {
        return object : AbstractIterator<T>() {
            private var hasSupplied = false

            override fun computeNext(): T? {
                if (!hasSupplied) {
                    hasSupplied = true
                    return supplier.get()
                } else {
                    return endOfData()
                }
            }
        }
    }
}
