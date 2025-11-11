/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.yaml

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.stream.MoreStreams
import java.io.*
import java.nio.charset.StandardCharsets
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class YamlsTest {
    @Test
    fun testSerialize() {
        Assertions.assertEquals(
            "$LINE_BREAK${STR_ABC}num: 999\nnumLong: 888\n",
            Yamls.serialize(ToClass(ABC, 999, 888L))
        )

        Assertions.assertEquals(
            "${LINE_BREAK}test: \"abc\"\ntest2: \"def\"\n",
            Yamls.serialize(ImmutableMap.of("test", ABC, "test2", "def"))
        )
    }

    @Test
    fun testSerializeWithoutQuotes() {
        Assertions.assertEquals(
            "${LINE_BREAK}str: abc\nnum: 999\nnumLong: 888\n",
            Yamls.serializeWithoutQuotes(ToClass(ABC, 999, 888L))
        )

        Assertions.assertEquals(
            "${LINE_BREAK}test: abc\ntest2: def\n",
            Yamls.serializeWithoutQuotes(ImmutableMap.of("test", ABC, "test2", "def"))
        )
    }

    @Test
    fun testSerializeJsonNode() {
        Assertions.assertEquals(
            "$LINE_BREAK${STR_ABC}num: 999\nnumLong: 888\n",
            Yamls.serialize(Jsons.jsonNode(ToClass(ABC, 999, 888L)))
        )

        Assertions.assertEquals(
            "${LINE_BREAK}test: \"abc\"\ntest2: \"def\"\n",
            Yamls.serialize(Jsons.jsonNode(ImmutableMap.of("test", ABC, "test2", "def")))
        )
    }

    @Test
    fun testDeserialize() {
        Assertions.assertEquals(
            ToClass(ABC, 999, 888L),
            Yamls.deserialize(
                "$LINE_BREAK${STR_ABC}num: \"999\"\nnumLong: \"888\"\n",
                ToClass::class.java
            )
        )
    }

    @Test
    fun testDeserializeToJsonNode() {
        Assertions.assertEquals(
            "{\"str\":\"abc\"}",
            Yamls.deserialize(LINE_BREAK + STR_ABC).toString()
        )

        Assertions.assertEquals(
            "[{\"str\":\"abc\"},{\"str\":\"abc\"}]",
            Yamls.deserialize("$LINE_BREAK- str: \"abc\"\n- str: \"abc\"\n").toString()
        )
    }

    @Test
    @Throws(Exception::class)
    fun testListWriter() {
        val values: List<Int> = Lists.newArrayList(1, 2, 3)
        val writer = Mockito.spy(StringWriter())
        val consumer = Yamls.listWriter<Int>(writer)
        values.forEach(consumer)
        consumer.close()

        Mockito.verify(writer).close()

        val deserialize: List<*> = Yamls.deserialize(writer.toString(), MutableList::class.java)
        Assertions.assertEquals(values, deserialize)
    }

    @Test
    @Throws(IOException::class)
    fun testStreamRead() {
        val classes: List<ToClass> =
            Lists.newArrayList(ToClass("1", 1, 1), ToClass("2", 2, 2), ToClass("3", 3, 3))
        val input =
            Mockito.spy(
                ByteArrayInputStream(Yamls.serialize(classes).toByteArray(StandardCharsets.UTF_8))
            )

        try {
            Yamls.deserializeArray(input).use { iterator ->
                Assertions.assertEquals(
                    classes,
                    MoreStreams.toStream(iterator)
                        .map { e: JsonNode -> Jsons.`object`(e, ToClass::class.java) }
                        .toList()
                )
            }
        } catch (e: Exception) {
            Assertions.fail<Any>()
        }

        Mockito.verify(input).close()
    }

    private class ToClass {
        @JsonProperty("str") var str: String? = null

        @JsonProperty("num") var num: Int? = null

        @JsonProperty("numLong") var numLong: Long = 0

        constructor()

        constructor(str: String?, num: Int?, numLong: Long) {
            this.str = str
            this.num = num
            this.numLong = numLong
        }

        override fun equals(o: Any?): Boolean {
            if (this === o) {
                return true
            }
            if (o == null || javaClass != o.javaClass) {
                return false
            }
            val toClass = o as ToClass
            return numLong == toClass.numLong && str == toClass.str && num == toClass.num
        }

        override fun hashCode(): Int {
            return Objects.hash(str, num, numLong)
        }
    }

    companion object {
        private const val LINE_BREAK = "---\n"
        private const val STR_ABC = "str: \"abc\"\n"
        private const val ABC = "abc"
    }
}
