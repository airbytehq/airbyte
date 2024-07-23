/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import datadog.trace.api.DDTags
import datadog.trace.api.interceptor.MutableSpan
import io.opentracing.Span
import io.opentracing.log.Fields
import io.opentracing.tag.Tags
import io.opentracing.util.GlobalTracer
import java.io.*
import java.util.function.Consumer

/** Collection of utility methods to help with performance tracing. */
object ApmTraceUtils {
    /** String format for the name of tags added to spans. */
    const val TAG_FORMAT: String = "airbyte.%s.%s"

    /** Standard prefix for tags added to spans. */
    const val TAG_PREFIX: String = "metadata"

    /**
     * Adds all provided tags to the currently active span, if one exists, under the provided tag
     * name namespace.
     *
     * @param tags A map of tags to be added to the currently active span.
     * @param tagPrefix The prefix to be added to each custom tag name.
     */
    /**
     * Adds all the provided tags to the currently active span, if one exists. <br></br> All tags
     * added via this method will use the default [.TAG_PREFIX] namespace.
     *
     * @param tags A map of tags to be added to the currently active span.
     */
    @JvmOverloads
    fun addTagsToTrace(tags: Map<String, Any>, tagPrefix: String? = TAG_PREFIX) {
        addTagsToTrace(GlobalTracer.get().activeSpan(), tags, tagPrefix)
    }

    /**
     * Adds all the provided tags to the provided span, if one exists.
     *
     * @param span The [Span] that will be associated with the tags.
     * @param tags A map of tags to be added to the currently active span.
     * @param tagPrefix The prefix to be added to each custom tag name.
     */
    fun addTagsToTrace(span: Span?, tags: Map<String, Any>, tagPrefix: String?) {
        if (span != null) {
            tags.entries.forEach(
                Consumer { entry: Map.Entry<String, Any> ->
                    span.setTag(formatTag(entry.key, tagPrefix), entry.value.toString())
                }
            )
        }
    }

    /**
     * Adds an exception to the currently active span, if one exists.
     *
     * @param t The [Throwable] to be added to the currently active span.
     */
    @JvmStatic
    fun addExceptionToTrace(t: Throwable?) {
        addExceptionToTrace(GlobalTracer.get().activeSpan(), t)
    }

    /**
     * Adds an exception to the provided span, if one exists.
     *
     * @param span The [Span] that will be associated with the exception.
     * @param t The [Throwable] to be added to the provided span.
     */
    fun addExceptionToTrace(span: Span?, t: Throwable?) {
        if (span != null) {
            span.setTag(Tags.ERROR, true)
            span.log(java.util.Map.of(Fields.ERROR_OBJECT, t))
        }
    }

    /**
     * Adds all the provided tags to the root span.
     *
     * @param tags A map of tags to be added to the root span.
     */
    fun addTagsToRootSpan(tags: Map<String, Any>) {
        val activeSpan = GlobalTracer.get().activeSpan()
        if (activeSpan is MutableSpan) {
            val localRootSpan = (activeSpan as MutableSpan).localRootSpan
            tags.entries.forEach(
                Consumer { entry: Map.Entry<String, Any> ->
                    localRootSpan.setTag(formatTag(entry.key, TAG_PREFIX), entry.value.toString())
                }
            )
        }
    }

    /**
     * Adds an exception to the root span, if an active one exists.
     *
     * @param t The [Throwable] to be added to the provided span.
     */
    fun recordErrorOnRootSpan(t: Throwable) {
        val activeSpan = GlobalTracer.get().activeSpan()
        if (activeSpan != null) {
            activeSpan.setTag(Tags.ERROR, true)
            activeSpan.log(java.util.Map.of(Fields.ERROR_OBJECT, t))
        }
        if (activeSpan is MutableSpan) {
            val localRootSpan = (activeSpan as MutableSpan).localRootSpan
            localRootSpan.setError(true)
            localRootSpan.setTag(DDTags.ERROR_MSG, t.message)
            localRootSpan.setTag(DDTags.ERROR_TYPE, t.javaClass.name)
            val errorString = StringWriter()
            t.printStackTrace(PrintWriter(errorString))
            localRootSpan.setTag(DDTags.ERROR_STACK, errorString.toString())
        }
    }

    /**
     * Formats the tag key using [.TAG_FORMAT] provided by this utility with the provided tag
     * prefix.
     *
     * @param tagKey The tag key to format.
     * @param tagPrefix The prefix to be added to each custom tag name.
     * @return The formatted tag key.
     */
    /**
     * Formats the tag key using [.TAG_FORMAT] provided by this utility, using the default tag
     * prefix [.TAG_PREFIX].
     *
     * @param tagKey The tag key to format.
     * @return The formatted tag key.
     */
    @JvmOverloads
    fun formatTag(tagKey: String?, tagPrefix: String? = TAG_PREFIX): String {
        return String.format(TAG_FORMAT, tagPrefix, tagKey)
    }
}
