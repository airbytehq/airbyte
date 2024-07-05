/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.json

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.node.BinaryNode
import com.google.common.base.Charsets
import com.google.common.collect.ImmutableList
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import com.google.common.collect.Sets
import java.nio.charset.StandardCharsets
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class JsonsTest {
    @Test
    fun testSerialize() {
        Assertions.assertEquals(SERIALIZED_JSON, Jsons.serialize(ToClass(ABC, 999, 888L)))

        Assertions.assertEquals(
            "{\"test\":\"abc\",\"test2\":\"def\"}",
            Jsons.serialize(ImmutableMap.of(TEST, ABC, TEST2, DEF))
        )
    }

    @Test
    fun testSerializeJsonNode() {
        Assertions.assertEquals(
            SERIALIZED_JSON,
            Jsons.serialize(Jsons.jsonNode(ToClass(ABC, 999, 888L)))
        )

        Assertions.assertEquals(
            "{\"test\":\"abc\",\"test2\":\"def\"}",
            Jsons.serialize(Jsons.jsonNode(ImmutableMap.of(TEST, ABC, TEST2, DEF)))
        )
        // issue: 5878 add test for binary node serialization, binary data are
        // serialized into base64
        Assertions.assertEquals(
            "{\"test\":\"dGVzdA==\"}",
            Jsons.serialize(
                Jsons.jsonNode(
                    ImmutableMap.of(TEST, BinaryNode("test".toByteArray(StandardCharsets.UTF_8)))
                )
            )
        )
    }

    @Test
    fun testDeserialize() {
        Assertions.assertEquals(
            ToClass(ABC, 999, 888L),
            Jsons.deserialize(
                "{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}",
                ToClass::class.java
            )
        )
    }

    @Test
    fun testDeserializeToJsonNode() {
        Assertions.assertEquals(SERIALIZED_JSON2, Jsons.deserialize(SERIALIZED_JSON2).toString())

        Assertions.assertEquals(
            "[{\"str\":\"abc\"},{\"str\":\"abc\"}]",
            Jsons.deserialize("[{\"str\":\"abc\"},{\"str\":\"abc\"}]").toString()
        )
        // issue: 5878 add test for binary node deserialization, for now should be
        // base64 string
        Assertions.assertEquals(
            "{\"test\":\"dGVzdA==\"}",
            Jsons.deserialize("{\"test\":\"dGVzdA==\"}").toString()
        )
    }

    @Test
    fun testTryDeserialize() {
        Assertions.assertEquals(
            Optional.of(ToClass(ABC, 999, 888L)),
            Jsons.tryDeserialize(
                "{\"str\":\"abc\", \"num\": 999, \"numLong\": 888}",
                ToClass::class.java
            )
        )

        Assertions.assertEquals(
            Optional.of(ToClass(ABC, 999, 0L)),
            Jsons.tryDeserialize(
                "{\"str\":\"abc\", \"num\": 999, \"test\": 888}",
                ToClass::class.java
            )
        )
    }

    @Test
    fun testTryDeserializeToJsonNode() {
        Assertions.assertEquals(
            Optional.of(Jsons.deserialize(SERIALIZED_JSON2)),
            Jsons.tryDeserialize(SERIALIZED_JSON2)
        )

        Assertions.assertEquals(
            Optional.empty<Any>(),
            Jsons.tryDeserialize("{\"str\":\"abc\", \"num\": 999, \"test}")
        )
    }

    @Test
    fun testToJsonNode() {
        Assertions.assertEquals(SERIALIZED_JSON, Jsons.jsonNode(ToClass(ABC, 999, 888L)).toString())

        Assertions.assertEquals(
            "{\"test\":\"abc\",\"test2\":\"def\"}",
            Jsons.jsonNode(ImmutableMap.of(TEST, ABC, TEST2, DEF)).toString()
        )

        Assertions.assertEquals(
            "{\"test\":\"abc\",\"test2\":{\"inner\":1}}",
            Jsons.jsonNode(ImmutableMap.of(TEST, ABC, TEST2, ImmutableMap.of("inner", 1)))
                .toString()
        )

        Assertions.assertEquals(
            Jsons.jsonNode(ToClass(ABC, 999, 888L)),
            Jsons.jsonNode(Jsons.jsonNode(ToClass(ABC, 999, 888L)))
        )
    }

    @Test
    fun testEmptyObject() {
        Assertions.assertEquals(Jsons.deserialize("{}"), Jsons.emptyObject())
    }

    @Test
    fun testArrayNode() {
        Assertions.assertEquals(Jsons.deserialize("[]"), Jsons.arrayNode())
    }

    @Test
    fun testToObject() {
        val expected = ToClass(ABC, 999, 888L)
        Assertions.assertEquals(
            expected,
            Jsons.`object`(Jsons.jsonNode(expected), ToClass::class.java)
        )

        Assertions.assertEquals(
            Lists.newArrayList(expected),
            Jsons.`object`<List<ToClass>>(
                Jsons.jsonNode(Lists.newArrayList(expected)),
                object : TypeReference<List<ToClass>>() {}
            )
        )

        Assertions.assertEquals(
            ToClass(),
            Jsons.`object`(Jsons.deserialize("{\"a\":1}"), ToClass::class.java)
        )
    }

    @Test
    fun testTryToObject() {
        val expected = ToClass(ABC, 999, 888L)
        Assertions.assertEquals(
            Optional.of(expected),
            Jsons.tryObject(Jsons.deserialize(SERIALIZED_JSON), ToClass::class.java)
        )

        Assertions.assertEquals(
            Optional.of(expected),
            Jsons.tryObject(
                Jsons.deserialize(SERIALIZED_JSON),
                object : TypeReference<ToClass>() {}
            )
        )

        val emptyExpected = ToClass()
        Assertions.assertEquals(
            Optional.of(emptyExpected),
            Jsons.tryObject(Jsons.deserialize("{\"str1\":\"abc\"}"), ToClass::class.java)
        )

        Assertions.assertEquals(
            Optional.of(emptyExpected),
            Jsons.tryObject(
                Jsons.deserialize("{\"str1\":\"abc\"}"),
                object : TypeReference<ToClass>() {}
            )
        )
    }

    @Test
    fun testClone() {
        val expected = ToClass("abc", 999, 888L)
        val actual = Jsons.clone(expected)
        Assertions.assertNotSame(expected, actual)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun testToBytes() {
        val jsonString = "{\"test\":\"abc\",\"type\":[\"object\"]}"
        Assertions.assertArrayEquals(
            jsonString.toByteArray(Charsets.UTF_8),
            Jsons.toBytes(Jsons.deserialize(jsonString))
        )
    }

    @Test
    fun testKeys() {
        // test object json node
        val jsonNode = Jsons.jsonNode(ImmutableMap.of(TEST, ABC, TEST2, DEF))
        Assertions.assertEquals(Sets.newHashSet(TEST, TEST2), Jsons.keys(jsonNode))

        // test literal jsonNode
        Assertions.assertEquals(emptySet<Any>(), Jsons.keys(jsonNode["test"]))

        // test nested object json node. should only return top-level keys.
        val nestedJsonNode =
            Jsons.jsonNode(ImmutableMap.of(TEST, ABC, TEST2, ImmutableMap.of("test3", "def")))
        Assertions.assertEquals(Sets.newHashSet(TEST, TEST2), Jsons.keys(nestedJsonNode))

        // test array json node
        val arrayJsonNode = Jsons.jsonNode(ImmutableList.of(ImmutableMap.of(TEST, ABC, TEST2, DEF)))
        Assertions.assertEquals(emptySet<Any>(), Jsons.keys(arrayJsonNode))
    }

    @Test
    fun testToPrettyString() {
        val jsonNode = Jsons.jsonNode(ImmutableMap.of(TEST, ABC))
        val expectedOutput = """{
  "test": "abc"
}
"""
        Assertions.assertEquals(expectedOutput, Jsons.toPrettyString(jsonNode))
    }

    @Test
    fun testGetOptional() {
        val json =
            Jsons.deserialize(
                "{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": {}, \"mno\": \"pqr\", \"stu\": null }"
            )

        Assertions.assertEquals(Optional.of(Jsons.jsonNode(GHI)), Jsons.getOptional(json, ABC, DEF))
        Assertions.assertEquals(Optional.of(Jsons.emptyObject()), Jsons.getOptional(json, JKL))
        Assertions.assertEquals(Optional.of(Jsons.jsonNode(PQR)), Jsons.getOptional(json, MNO))
        Assertions.assertEquals(
            Optional.of(Jsons.jsonNode<Any?>(null)),
            Jsons.getOptional(json, STU)
        )
        Assertions.assertEquals(Optional.empty<Any>(), Jsons.getOptional(json, XYZ))
        Assertions.assertEquals(Optional.empty<Any>(), Jsons.getOptional(json, ABC, XYZ))
        Assertions.assertEquals(Optional.empty<Any>(), Jsons.getOptional(json, ABC, DEF, XYZ))
        Assertions.assertEquals(Optional.empty<Any>(), Jsons.getOptional(json, ABC, JKL, XYZ))
        Assertions.assertEquals(Optional.empty<Any>(), Jsons.getOptional(json, STU, XYZ))
    }

    @Test
    fun testGetStringOrNull() {
        val json =
            Jsons.deserialize("{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": \"mno\", \"pqr\": 1 }")

        Assertions.assertEquals(GHI, Jsons.getStringOrNull(json, ABC, DEF))
        Assertions.assertEquals(MNO, Jsons.getStringOrNull(json, JKL))
        Assertions.assertEquals("1", Jsons.getStringOrNull(json, PQR))
        Assertions.assertNull(Jsons.getStringOrNull(json, ABC, DEF, XYZ))
        Assertions.assertNull(Jsons.getStringOrNull(json, XYZ))
    }

    @Test
    fun testGetEstimatedByteSize() {
        val json =
            Jsons.deserialize("{\"string_key\":\"abc\",\"array_key\":[\"item1\", \"item2\"]}")
        Assertions.assertEquals(Jsons.toBytes(json).size, Jsons.getEstimatedByteSize(json))
    }

    @Test
    fun testFlatten__noArrays() {
        val json = Jsons.deserialize("{ \"abc\": { \"def\": \"ghi\" }, \"jkl\": true, \"pqr\": 1 }")
        val expected =
            Stream.of(
                    *arrayOf(
                        arrayOf<Any>("abc.def", GHI),
                        arrayOf<Any>(JKL, true),
                        arrayOf<Any>(PQR, 1),
                    )
                )
                .collect(
                    Collectors.toMap(
                        Function { data: Array<Any> -> data[0] as String },
                        Function { data: Array<Any> -> data[1] }
                    )
                )
        Assertions.assertEquals(expected, Jsons.flatten(json, false))
    }

    @Test
    fun testFlatten__withArraysNoApplyFlatten() {
        val json =
            Jsons.deserialize(
                "{ \"abc\": [{ \"def\": \"ghi\" }, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }"
            )
        val expected =
            Stream.of(
                    *arrayOf(
                        arrayOf<Any>(ABC, "[{\"def\":\"ghi\"},{\"fed\":\"ihg\"}]"),
                        arrayOf<Any>(JKL, true),
                        arrayOf<Any>(PQR, 1),
                    )
                )
                .collect(
                    Collectors.toMap(
                        Function { data: Array<Any> -> data[0] as String },
                        Function { data: Array<Any> -> data[1] }
                    )
                )
        Assertions.assertEquals(expected, Jsons.flatten(json, false))
    }

    @Test
    fun testFlatten__checkBackwardCompatiblity() {
        val json =
            Jsons.deserialize(
                "{ \"abc\": [{ \"def\": \"ghi\" }, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }"
            )
        val expected =
            Stream.of(
                    *arrayOf(
                        arrayOf<Any>(ABC, "[{\"def\":\"ghi\"},{\"fed\":\"ihg\"}]"),
                        arrayOf<Any>(JKL, true),
                        arrayOf<Any>(PQR, 1),
                    )
                )
                .collect(
                    Collectors.toMap(
                        Function { data: Array<Any> -> data[0] as String },
                        Function { data: Array<Any> -> data[1] }
                    )
                )
        Assertions.assertEquals(expected, Jsons.flatten(json))
    }

    @Test
    fun testFlatten__withArraysApplyFlatten() {
        val json =
            Jsons.deserialize(
                "{ \"abc\": [{ \"def\": \"ghi\" }, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }"
            )
        val expected =
            Stream.of(
                    *arrayOf(
                        arrayOf<Any>("abc.[0].def", "ghi"),
                        arrayOf<Any>("abc.[1].fed", "ihg"),
                        arrayOf<Any>(JKL, true),
                        arrayOf<Any>(PQR, 1),
                    )
                )
                .collect(
                    Collectors.toMap(
                        Function { data: Array<Any> -> data[0] as String },
                        Function { data: Array<Any> -> data[1] }
                    )
                )
        Assertions.assertEquals(expected, Jsons.flatten(json, true))
    }

    @Test
    fun testFlatten__withArraysApplyFlattenNested() {
        val json =
            Jsons.deserialize(
                "{ \"abc\": [{ \"def\": {\"ghi\": [\"xyz\"] }}, { \"fed\": \"ihg\" }], \"jkl\": true, \"pqr\": 1 }"
            )
        val expected =
            Stream.of(
                    *arrayOf(
                        arrayOf<Any>("abc.[0].def.ghi.[0]", "xyz"),
                        arrayOf<Any>("abc.[1].fed", "ihg"),
                        arrayOf<Any>(JKL, true),
                        arrayOf<Any>(PQR, 1),
                    )
                )
                .collect(
                    Collectors.toMap(
                        Function { data: Array<Any> -> data[0] as String },
                        Function { data: Array<Any> -> data[1] }
                    )
                )
        Assertions.assertEquals(expected, Jsons.flatten(json, true))
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
        private const val SERIALIZED_JSON = "{\"str\":\"abc\",\"num\":999,\"numLong\":888}"
        private const val SERIALIZED_JSON2 = "{\"str\":\"abc\"}"
        private const val ABC = "abc"
        private const val DEF = "def"
        private const val GHI = "ghi"
        private const val JKL = "jkl"
        private const val MNO = "mno"
        private const val PQR = "pqr"
        private const val STU = "stu"
        private const val TEST = "test"
        private const val TEST2 = "test2"
        private const val XYZ = "xyz"
    }
}
