/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.featureflag

import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class MultiTest {
    @Test
    fun `verify data`() {
        val source = Source("source")
        val workspace = Workspace("workspace")

        Multi(listOf(source, workspace)).also {
            assert(it.kind == "multi")
        }
    }

    @Test
    fun `Multi cannot contain another Multi`() {
        val source = Source("source")
        val workspace = Workspace("workspace")
        val multi = Multi(listOf(source, workspace))

        assertFailsWith<IllegalArgumentException> {
            Multi(listOf(source, workspace, multi))
        }
    }

    @Test
    fun `fetchContexts returns correct results`() {
        val source1 = Source("source1")
        val source2 = Source("source2")
        val workspace = Workspace("workspace")
        val multi = Multi(listOf(source1, source2, workspace))

        assertEquals(listOf(source1, source2), multi.fetchContexts(), "two source contexts")
        assertEquals(listOf(workspace), multi.fetchContexts(), "one workspace context")
        assertEquals(listOf(), multi.fetchContexts<Connection>(), "should be empty as no connection context was provided")
    }

    @Test
    fun `key set correctly based on contexts`() {
        val workspace = Workspace("workspace")
        val connection = Connection("connection")
        val source = Source("source")
        val destination = Destination("destination")
        val user = User("user")

        Multi(listOf(user, destination, source, connection, workspace)).also {
            assert(it.key == workspace.key)
        }
        Multi(listOf(user, destination, source, connection)).also {
            assert(it.key == connection.key)
        }
        Multi(listOf(user, destination, source)).also {
            assert(it.key == source.key)
        }
        Multi(listOf(user, destination)).also {
            assert(it.key == destination.key)
        }
        Multi(listOf(user)).also {
            assert(it.key == user.key)
        }
    }

    @Test
    fun `no contexts is an exception`() {
        assertFailsWith<IllegalArgumentException> {
            Multi(listOf())
        }
    }
}

class WorkspaceTest {
    @Test
    fun `verify data`() {
        Workspace("workspace key", "user").also {
            assert(it.kind == "workspace")
            assert(it.key == "workspace key")
            assert(it.user == "user")
        }
    }
}

class UserTest {
    @Test
    fun `verify data`() {
        User("user key").also {
            assert(it.kind == "user")
            assert(it.key == "user key")
        }
    }
}

class ConnectionTest {
    @Test
    fun `verify data`() {
        Connection("connection key").also {
            assert(it.kind == "connection")
            assert(it.key == "connection key")
        }
    }
}

class SourceTest {
    @Test
    fun `verify data`() {
        Source("source key").also {
            assert(it.kind == "source")
            assert(it.key == "source key")
        }
    }
}

class DestinationTest {
    @Test
    fun `verify data`() {
        Destination("destination key").also {
            assert(it.kind == "destination")
            assert(it.key == "destination key")
        }
    }
}
