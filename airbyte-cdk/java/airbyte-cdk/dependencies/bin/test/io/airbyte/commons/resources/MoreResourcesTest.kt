/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.resources

import com.google.common.collect.Sets
import io.airbyte.commons.io.IOs
import java.io.IOException
import java.net.URISyntaxException
import java.nio.charset.StandardCharsets
import java.nio.file.Path
import java.util.stream.Collectors
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class MoreResourcesTest {
    @Test
    @Throws(IOException::class)
    fun testResourceRead() {
        Assertions.assertEquals(CONTENT_1, MoreResources.readResource(RESOURCE_TEST))
        Assertions.assertEquals(CONTENT_2, MoreResources.readResource("subdir/resource_test_sub"))

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            MoreResources.readResource("invalid")
        }
    }

    @Test
    @Throws(IOException::class)
    fun testResourceReadWithClass() {
        Assertions.assertEquals(
            CONTENT_1,
            MoreResources.readResource(MoreResourcesTest::class.java, RESOURCE_TEST)
        )
        Assertions.assertEquals(
            CONTENT_2,
            MoreResources.readResource(MoreResourcesTest::class.java, "subdir/resource_test_sub")
        )

        Assertions.assertEquals(
            CONTENT_1,
            MoreResources.readResource(MoreResourcesTest::class.java, "/resource_test")
        )
        Assertions.assertEquals(
            CONTENT_2,
            MoreResources.readResource(MoreResourcesTest::class.java, "/subdir/resource_test_sub")
        )

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            MoreResources.readResource(MoreResourcesTest::class.java, "invalid")
        }
    }

    @Test
    @Throws(URISyntaxException::class)
    fun testReadResourceAsFile() {
        val file = MoreResources.readResourceAsFile(RESOURCE_TEST)
        Assertions.assertEquals(CONTENT_1, IOs.readFile(file.toPath()))
    }

    @Test
    @Throws(IOException::class)
    fun testReadBytes() {
        Assertions.assertEquals(
            CONTENT_1,
            String(MoreResources.readBytes(RESOURCE_TEST), StandardCharsets.UTF_8)
        )
        Assertions.assertEquals(
            CONTENT_2,
            String(MoreResources.readBytes("subdir/resource_test_sub"), StandardCharsets.UTF_8)
        )

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            MoreResources.readBytes("invalid")
        }
    }

    @Test
    @Throws(IOException::class)
    fun testResourceReadDuplicateName() {
        Assertions.assertEquals(CONTENT_1, MoreResources.readResource("resource_test_a"))
        Assertions.assertEquals(CONTENT_2, MoreResources.readResource("subdir/resource_test_a"))
    }

    @Test
    @Throws(IOException::class)
    fun testListResource() {
        Assertions.assertEquals(
            Sets.newHashSet(
                "subdir",
                "resource_test_sub",
                "resource_test_sub_2",
                "resource_test_a"
            ),
            MoreResources.listResources(MoreResourcesTest::class.java, "subdir")
                .map { obj: Path -> obj.fileName }
                .map { obj: Path -> obj.toString() }
                .collect(Collectors.toSet())
        )
    }

    companion object {
        private const val CONTENT_1 = "content1\n"
        private const val CONTENT_2 = "content2\n"
        private const val RESOURCE_TEST = "resource_test"
    }
}
