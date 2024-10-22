/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.enums

import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class EnumsTest {
    internal enum class E1 {
        TEST,
        TEST2
    }

    internal enum class E2 {
        TEST
    }

    internal enum class E3 {
        TEST,
        TEST2
    }

    internal enum class E4 {
        TEST,
        TEST3
    }

    @Test
    fun testConversion() {
        Assertions.assertEquals(E2.TEST, Enums.convertTo(E1.TEST, E2::class.java))
    }

    @Test
    fun testConversionFails() {
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            Enums.convertTo(E1.TEST2, E2::class.java)
        }
    }

    @Test
    fun testSelfCompatible() {
        Assertions.assertTrue(Enums.isCompatible(E1::class.java, E1::class.java))
    }

    @Test
    fun testIsCompatible() {
        Assertions.assertTrue(Enums.isCompatible(E1::class.java, E3::class.java))
    }

    @Test
    fun testNotCompatibleDifferentNames() {
        Assertions.assertFalse(Enums.isCompatible(E1::class.java, E4::class.java))
    }

    @Test
    fun testNotCompatibleDifferentLength() {
        Assertions.assertFalse(Enums.isCompatible(E1::class.java, E4::class.java))
    }

    @Test
    fun testNotCompatibleDifferentLength2() {
        Assertions.assertFalse(Enums.isCompatible(E4::class.java, E1::class.java))
    }

    internal enum class E5 {
        VALUE_1,
        VALUE_TWO,
        value_three,
        value_4
    }

    @Test
    fun testToEnum() {
        Assertions.assertEquals(Optional.of(E1.TEST), Enums.toEnum("test", E1::class.java))
        Assertions.assertEquals(Optional.of(E5.VALUE_1), Enums.toEnum("VALUE_1", E5::class.java))
        Assertions.assertEquals(Optional.of(E5.VALUE_1), Enums.toEnum("value_1", E5::class.java))
        Assertions.assertEquals(
            Optional.of(E5.VALUE_TWO),
            Enums.toEnum("VALUE_TWO", E5::class.java)
        )
        Assertions.assertEquals(Optional.of(E5.VALUE_TWO), Enums.toEnum("valuetwo", E5::class.java))
        Assertions.assertEquals(Optional.of(E5.VALUE_TWO), Enums.toEnum("valueTWO", E5::class.java))
        Assertions.assertEquals(
            Optional.of(E5.VALUE_TWO),
            Enums.toEnum("valueTWO$", E5::class.java)
        )
        Assertions.assertEquals(
            Optional.of(E5.VALUE_TWO),
            Enums.toEnum("___valueTWO___", E5::class.java)
        )
        Assertions.assertEquals(
            Optional.of(E5.value_three),
            Enums.toEnum("VALUE_THREE", E5::class.java)
        )
        Assertions.assertEquals(Optional.of(E5.value_4), Enums.toEnum("VALUE_4", E5::class.java))
        Assertions.assertEquals(Optional.empty<Any>(), Enums.toEnum("VALUE_5", E5::class.java))
    }
}
