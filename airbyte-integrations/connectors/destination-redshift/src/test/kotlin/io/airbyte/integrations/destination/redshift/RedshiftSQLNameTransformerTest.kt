/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class RedshiftSQLNameTransformerTest {
    private val transformer = RedshiftSQLNameTransformer()

    @Test
    fun testBasicAsciiNames() {
        assertEquals("my_table", transformer.convertStreamName("my_table"))
        assertEquals("mytable", transformer.convertStreamName("MyTable"))
        assertEquals("my_table_123", transformer.convertStreamName("my_table_123"))
    }

    @Test
    fun testSpacesReplacedWithUnderscores() {
        assertEquals("my_table_name", transformer.convertStreamName("my table name"))
        assertEquals("table_with_spaces", transformer.convertStreamName("table  with   spaces"))
    }

    @Test
    fun testJapaneseCharacters() {
        // タイプ - All 3-byte UTF-8 characters
        assertEquals("タイプ", transformer.convertStreamName("タイプ"))
        assertEquals("テーブル名", transformer.convertStreamName("テーブル名"))
    }

    @Test
    fun testArabicCharacters() {
        // تاريخ - All 2-byte UTF-8 characters
        assertEquals("تاريخ", transformer.convertStreamName("تاريخ"))
        // Space should be replaced with underscore
        assertEquals("تاريخ_الميلاد", transformer.convertStreamName("تاريخ الميلاد"))
    }

    @Test
    fun testHindiCharacters() {
        // अनाप्लान - All 3-byte UTF-8 characters
        assertEquals("अनाप्लान", transformer.convertStreamName("अनाप्लान"))
    }

    @Test
    fun testMixedUnicodeAndAscii() {
        assertEquals("user_タイプ", transformer.convertStreamName("user_タイプ"))
        assertEquals("table_تاريخ", transformer.convertStreamName("table_تاريخ"))
        assertEquals("data_अनाप्लान", transformer.convertStreamName("data_अनाप्लान"))
    }

    @Test
    fun testLeadingDigit() {
        // Names starting with digits should be prefixed with underscore
        assertEquals("_123table", transformer.convertStreamName("123table"))
        assertEquals("_1タイプ", transformer.convertStreamName("1タイプ"))
    }

    @Test
    fun testSpecialCharactersReplaced() {
        assertEquals("my_table_name", transformer.convertStreamName("my@table#name"))
        assertEquals("table_name", transformer.convertStreamName("table!name"))
        assertEquals("test_table", transformer.convertStreamName("test-table"))
    }

    @Test
    fun testDollarSignAllowed() {
        // Dollar sign is allowed in subsequent positions
        assertEquals("table_$money", transformer.convertStreamName("table_$money"))
        // But not as first character
        assertEquals("_$money", transformer.convertStreamName("$money"))
    }

    @Test
    fun testUnderscorePreserved() {
        assertEquals("_my_table_", transformer.convertStreamName("_my_table_"))
        assertEquals("___", transformer.convertStreamName("___"))
    }

    @Test
    fun testMaxLength127Bytes() {
        // Create a string that would exceed 127 bytes
        // Each Japanese character is 3 bytes in UTF-8
        val longJapaneseName = "あ".repeat(50) // 50 * 3 = 150 bytes
        val result = transformer.convertStreamName(longJapaneseName)
        
        // Verify the result doesn't exceed 127 bytes
        val byteLength = result.toByteArray(Charsets.UTF_8).size
        assertTrue(byteLength <= 127, "Result byte length $byteLength exceeds 127 bytes")
        
        // Should contain 42 characters (42 * 3 = 126 bytes)
        assertEquals(42, result.length)
    }

    @Test
    fun testMaxLengthWithMixedCharacters() {
        // Mix of 1-byte (ASCII) and 3-byte (Japanese) characters
        val mixedName = "a".repeat(100) + "あ".repeat(20) // 100 + 60 = 160 bytes
        val result = transformer.convertStreamName(mixedName)
        
        val byteLength = result.toByteArray(Charsets.UTF_8).size
        assertTrue(byteLength <= 127, "Result byte length $byteLength exceeds 127 bytes")
    }

    @Test
    fun testEmptyString() {
        // Empty string should result in empty string (or could be handled differently)
        val result = transformer.convertStreamName("")
        assertTrue(result.isEmpty() || result == "_")
    }

    @Test
    fun testOnlySpecialCharacters() {
        // String with only special characters should be converted to underscores
        assertEquals("___", transformer.convertStreamName("@#$"))
        assertEquals("_", transformer.convertStreamName("!"))
    }

    @Test
    fun testLowercaseConversion() {
        // All names should be lowercased
        assertEquals("mytable", transformer.convertStreamName("MYTABLE"))
        assertEquals("mytable", transformer.convertStreamName("MyTable"))
        // Unicode characters should also be lowercased where applicable
        assertEquals("table", transformer.convertStreamName("TABLE"))
    }

    @Test
    fun testRealWorldExamplesFromBugReport() {
        // These are the exact examples from the bug report
        assertEquals("タイプ", transformer.convertStreamName("タイプ"))
        assertEquals("تاريخ_الميلاد", transformer.convertStreamName("تاريخ الميلاد"))
        assertEquals("अनाप्लान", transformer.convertStreamName("अनाप्लान"))
        
        // Verify these are NOT converted to underscores
        val result1 = transformer.convertStreamName("タイプ")
        assertTrue(result1.contains("タ") || result1.contains("イ") || result1.contains("プ"),
            "Japanese characters should be preserved, got: $result1")
        
        val result2 = transformer.convertStreamName("تاريخ الميلاد")
        assertTrue(result2.contains("ت") || result2.contains("ا") || result2.contains("ر"),
            "Arabic characters should be preserved, got: $result2")
        
        val result3 = transformer.convertStreamName("अनाप्लान")
        assertTrue(result3.contains("अ") || result3.contains("न") || result3.contains("ा"),
            "Hindi characters should be preserved, got: $result3")
    }

    @Test
    fun testChineseCharacters() {
        assertEquals("用户表", transformer.convertStreamName("用户表"))
        assertEquals("数据_表", transformer.convertStreamName("数据 表"))
    }

    @Test
    fun testKoreanCharacters() {
        assertEquals("테이블", transformer.convertStreamName("테이블"))
        assertEquals("사용자_데이터", transformer.convertStreamName("사용자 데이터"))
    }

    @Test
    fun testGreekCharacters() {
        assertEquals("πίνακας", transformer.convertStreamName("πίνακας"))
        assertEquals("δεδομένα", transformer.convertStreamName("δεδομένα"))
    }

    @Test
    fun testCyrillicCharacters() {
        assertEquals("таблица", transformer.convertStreamName("таблица"))
        assertEquals("данные", transformer.convertStreamName("данные"))
    }

    @Test
    fun testGetIdentifier() {
        // Test the getIdentifier method which should use convertStreamName
        assertEquals("タイプ", transformer.getIdentifier("タイプ"))
        assertEquals("my_table", transformer.getIdentifier("my_table"))
    }

    @Test
    fun testGetNamespace() {
        // Test the getNamespace method which should use convertStreamName
        assertEquals("my_schema", transformer.getNamespace("my_schema"))
        assertEquals("スキーマ", transformer.getNamespace("スキーマ"))
    }
}
