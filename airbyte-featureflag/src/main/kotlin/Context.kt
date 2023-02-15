/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag

import java.util.*

/**
 * Anonymous UUID to be used with anonymous contexts.
 *
 * Annotated with @JvmField for java interop.
 */
@JvmField
val ANONYMOUS = UUID(0, 0)

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

    /**
     * Multi contexts don't have a key, however for LDv5 reasons, a key must exist.
     *
     * Determine what the key should be based on the priority order of:
     * workspace -> connection -> source -> destination -> user
     * taking the first value
     *
     * When LDv5 support is dropped replace this with: override vale key = ""
     */
    override val key = when {
        /** Intellij is going to recommend replacing .sortedBy with .minByOrNull, ignore this recommendation. */
        fetchContexts<Workspace>().isNotEmpty() -> fetchContexts<Workspace>().sortedBy { it.key }.first().key
        fetchContexts<Connection>().isNotEmpty() -> fetchContexts<Connection>().sortedBy { it.key }.first().key
        fetchContexts<Source>().isNotEmpty() -> fetchContexts<Source>().sortedBy { it.key }.first().key
        fetchContexts<Destination>().isNotEmpty() -> fetchContexts<Destination>().sortedBy { it.key }.first().key
        fetchContexts<User>().isNotEmpty() -> fetchContexts<User>().sortedBy { it.key }.first().key
        else -> throw IllegalArgumentException("unsupported context: ${contexts.joinToString { it.kind }}")
    }

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

    /**
     * Secondary constructor
     *
     * @param [key] workspace UUID
     * @param [user] an optional user identifier
     */
    @JvmOverloads
    constructor(key: UUID, user: String? = null) : this(key = key.toString(), user = user)
}

/**
 * Context for representing a user.
 *
 * @param [key] the unique identifying value of this user
 */
data class User(override val key: String) : Context {
    override val kind = "user"

    /**
     * Secondary constructor
     *
     * @param [key] user UUID
     */
    constructor(key: UUID) : this(key = key.toString())
}

/**
 * Context for representing a connection.
 *
 * @param [key] the unique identifying value of this connection
 */
data class Connection(override val key: String) : Context {
    override val kind = "connection"

    /**
     * Secondary constructor
     *
     * @param [key] connection UUID
     */
    constructor(key: UUID) : this(key = key.toString())
}

/**
 * Context for representing a source.
 *
 * @param [key] the unique identifying value of this source
 */
data class Source(override val key: String) : Context {
    override val kind = "source"

    /**
     * Secondary constructor
     *
     * @param [key] Source UUID
     */
    constructor(key: UUID) : this(key = key.toString())
}

/**
 * Context for representing a destination.
 *
 * @param [key] the unique identifying value of this destination
 */
data class Destination(override val key: String) : Context {
    override val kind = "destination"

    /**
     * Secondary constructor
     *
     * @param [key] Destination UUID
     */
    constructor(key: UUID) : this(key = key.toString())
}
