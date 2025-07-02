/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.cdk

import kotlin.reflect.KClass
import org.testcontainers.containers.JdbcDatabaseContainer

data class NamespacedContainer<C>(val container: C, private val testClass: KClass<*>) where
C : JdbcDatabaseContainer<C> {

    val namespace: String
        get() = "s" + testClass.qualifiedName.hashCode().toString()
}
