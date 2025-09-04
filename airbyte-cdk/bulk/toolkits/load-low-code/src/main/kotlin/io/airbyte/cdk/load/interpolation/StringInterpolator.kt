/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.interpolation

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.module.kotlin.jacksonTypeRef
import com.hubspot.jinjava.Jinjava
import com.hubspot.jinjava.JinjavaConfig
import com.hubspot.jinjava.el.JinjavaInterpreterResolver
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.util.Jsons
import java.beans.FeatureDescriptor
import jinjava.javax.el.CompositeELResolver
import jinjava.javax.el.ELContext
import jinjava.javax.el.ELResolver
import jinjava.javax.el.PropertyNotWritableException

/**
 * This class allows for Kotlin/Python-like map accessor. Without this, the users of the low-code
 * language would need to use textual operator `get` (which is still allowed, but less expressive).
 * Given this class is registered as an ELResolver in the JinjavaConfig, the user will be able to
 * write `node["field"]` instead of `node.get("field").
 */
@SuppressFBWarnings(
    "NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE",
    justification =
        "The param in getValue needs to be nullable because it's a Java class but we fail if it's null"
)
private class MapGetOperatorELResolver : ELResolver() {
    override fun getCommonPropertyType(context: ELContext?, base: Any?): Class<*>? {
        return if (isBaseValid(base)) {
            String::class.java
        } else null
    }

    override fun getFeatureDescriptors(
        context: ELContext?,
        base: Any?
    ): Iterator<FeatureDescriptor?>? {
        return null
    }

    override fun getType(context: ELContext?, base: Any?, property: Any?): Class<*>? {
        return getValue(context, base, property)?.javaClass ?: Unit.javaClass
    }

    override fun getValue(context: ELContext?, base: Any?, property: Any?): Any? {
        if (context == null) {
            throw NullPointerException("context is null")
        } else {
            if (this.isResolvable(base, property)) {
                val value = (base as Map<*, *>).get(property as String)
                context.isPropertyResolved = true
                return value
            }

            return null
        }
    }

    override fun isReadOnly(p0: ELContext?, p1: Any?, p2: Any?): Boolean = true

    override fun setValue(p0: ELContext?, p1: Any?, p2: Any?, p3: Any?) {
        throw PropertyNotWritableException("resolver is read-only")
    }

    private fun isResolvable(base: Any?, property: Any?): Boolean {
        val baseValid = isBaseValid(base)
        val propertyValid = property != null && property is String
        return baseValid and propertyValid
    }

    private fun isBaseValid(base: Any?): Boolean = base != null && base is Map<*, *>
}

class StringInterpolator {
    private val interpolator =
        Jinjava(
            JinjavaConfig.newBuilder()
                .withElResolver(
                    CompositeELResolver().apply {
                        this.add(MapGetOperatorELResolver())
                        this.add(JinjavaInterpreterResolver.DEFAULT_RESOLVER_READ_ONLY)
                    }
                )
                .build()
        )

    /** Possible improvement: validate if all variables have been resolved and if not, throw. */
    fun interpolate(string: String, context: Map<String, Any>): String {
        return interpolator.render(string, context)
    }
}

fun JsonNode.toInterpolationContext(): Any = Jsons.convertValue(this, jacksonTypeRef<Any>())
