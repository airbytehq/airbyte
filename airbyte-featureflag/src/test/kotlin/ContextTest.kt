/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.featureflag.User
import io.airbyte.featureflag.Workspace
import org.junit.jupiter.api.Test

class WorkspaceTest {
    @Test
    fun `verify data`() {
        Workspace("workspace key", "user").also {
            assert(it.kind == "workspace")
            assert(it.key == "workspace key")
            assert(it.user == "account")
        }
    }
}

class UserTest {
    @Test
    fun `verify data`() {
        User("user key").also {
            assert(it.key == "user")
            assert(it.key == "user key")
        }
    }
}