/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag

/**
 * Context abstraction around LaunchDarkly v6 context idea
 *
 * I'm still playing around with this.  Basically the idea is to define our own custom context types
 * (by implementing this sealed interface) to ensure that we are consistently using the same identifiers
 * throughout the code.
 *
 * @property [kind] determines the kind of context the implementation is,
 * must be consistent for each type and should not be set by the caller of a context
 * @property [key] is the unique identifier for the specific context, e.g. a user-id or workspace-id
 */
sealed interface Context {
    val kind: String
    val key: String
}

/**
 * Context for representing multiple contexts concurrently.  Only supported for LaunchDarkly v6!
 *
 *  @param [contexts] list of contexts, must not contain another Multi context
 */
data class Multi(val contexts: List<Context>) : Context {
    /** This value MUST be "multi" to properly sync with the LaunchDarkly client. */
    override val kind = "multi"

    /** Multi contexts don't have a key */
    override val key = ""

    init {
        // ensure there are no nested contexts (i.e. this Multi does not contain another Multi)
        if (fetchContexts<Multi>().isNotEmpty()) {
            throw IllegalArgumentException("Multi contexts cannot be nested")
        }
    }

    /**
     * Returns all the [Context] types contained within this [Multi] matching type [T].
     *
     * @param [T] the [Context] type to fetch.
     * @return all [Context] of [T] within this [Multi], or an empty list if none match.
     */
    internal inline fun <reified T> fetchContexts(): List<T> {
        return contexts.filterIsInstance<T>()
    }
}

/**
 * Context for representing a workspace.
 *
 * @param [key] the unique identifying value of this workspace
 * @param [user] an optional user identifier
 */
data class Workspace @JvmOverloads constructor(
    override val key: String,
    val user: String? = null
) : Context {
    override val kind = "workspace"
}

/**
 * Context for representing a user.
 *
 * @param [key] the unique identifying value of this user
 */
data class User(override val key: String) : Context {
    override val kind = "user"
}

/**
 * Context for representing a connection.
 *
 * @param [key] the unique identifying value of this connection
 */
data class Connection(override val key: String) : Context {
    override val kind = "connection"
}

/**
 * Context for representing a source.
 *
 * @param [key] the unique identifying value of this source
 */
data class Source(override val key: String) : Context {
    override val kind = "source"
}

/**
 * Context for representing a destination.
 *
 * @param [key] the unique identifying value of this destination
 */
data class Destination(override val key: String) : Context {
    override val kind = "destination"
}