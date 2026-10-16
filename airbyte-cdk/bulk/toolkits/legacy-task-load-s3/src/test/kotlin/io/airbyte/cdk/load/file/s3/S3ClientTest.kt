/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.s3

import io.airbyte.cdk.load.command.s3.S3AddressingStyle
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class S3ClientTest {

    @Test
    fun `path style forces path-style requests`() {
        assertTrue(S3AddressingStyle.PATH_STYLE.shouldForcePathStyle())
    }

    @Test
    fun `virtual hosted style does not force path-style requests`() {
        assertFalse(S3AddressingStyle.VIRTUAL_HOSTED_STYLE.shouldForcePathStyle())
    }
}
