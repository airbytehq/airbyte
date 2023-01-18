/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.featureflag.Connection
import io.airbyte.featureflag.Destination
import io.airbyte.featureflag.Multi
import io.airbyte.featureflag.Source
import io.airbyte.featureflag.User
import io.airbyte.featureflag.Workspace
import org.junit.jupiter.api.Test

class MultiTest {
    @Test
    fun `verify data`() {
        val user = User("user-id")
        val workspace = Workspace("workspace")

        Multi(listOf(user, workspace)).also {
            assert(it.kind == "multi")
            assert(it.key == "")
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
