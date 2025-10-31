/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.text.Normalizer
import java.util.*

class RedshiftSQLNameTransformer : StandardNameTransformer() {
    override fun convertStreamName(input: String): String {
        return toRedshiftIdentifier(input)
    }

    /**
     * Converts a string to a valid Redshift identifier following AWS Redshift naming conventions.
     * 
     * Redshift standard identifiers support:
     * - Begin with an ASCII letter, underscore, or UTF-8 multibyte character (2-4 bytes)
     * - Subsequent characters can be ASCII letters, digits, underscores, dollar signs, or UTF-8 multibyte characters (2-4 bytes)
     * - Maximum 127 bytes in UTF-8 encoding
     * - No spaces or quotes
     * 
     * See: https://docs.aws.amazon.com/redshift/latest/dg/r_names.html
     */
    private fun toRedshiftIdentifier(input: String): String {
        // Normalize to NFC form to ensure consistent representation
        val normalized = Normalizer.normalize(input, Normalizer.Form.NFC)
        
        // Replace spaces with underscores (spaces not allowed in standard identifiers)
        val spacesReplaced = normalized.replace("\\s+".toRegex(), "_")
        
        val result = StringBuilder()
        var byteCount = 0
        
        for (i in spacesReplaced.indices) {
            val codePoint = spacesReplaced.codePointAt(i)
            val char = spacesReplaced[i]
            
            // Calculate UTF-8 byte length for this code point
            val charByteLength = when {
                codePoint <= 0x7F -> 1
                codePoint <= 0x7FF -> 2
                codePoint <= 0xFFFF -> 3
                else -> 4
            }
            
            // Check if adding this character would exceed 127 bytes
            if (byteCount + charByteLength > 127) {
                break
            }
            
            // First character rules
            if (result.isEmpty()) {
                when {
                    // Allow ASCII letters, underscore, or Unicode letters
                    char == '_' || Character.isLetter(codePoint) -> {
                        result.appendCodePoint(codePoint)
                        byteCount += charByteLength
                    }
                    // If starts with digit or other invalid character, prefix with underscore
                    else -> {
                        result.append('_')
                        byteCount += 1
                        // Try to add the original character if it's valid for subsequent positions
                        if (Character.isLetterOrDigit(codePoint) || char == '_' || char == '$') {
                            if (byteCount + charByteLength <= 127) {
                                result.appendCodePoint(codePoint)
                                byteCount += charByteLength
                            }
                        }
                    }
                }
            } else {
                // Subsequent character rules: allow letters, digits, underscore, dollar sign
                when {
                    Character.isLetterOrDigit(codePoint) || char == '_' || char == '$' -> {
                        result.appendCodePoint(codePoint)
                        byteCount += charByteLength
                    }
                    // Replace invalid characters with underscore
                    else -> {
                        if (byteCount + 1 <= 127) {
                            result.append('_')
                            byteCount += 1
                        }
                    }
                }
            }
            
            // Skip the low surrogate if this was a surrogate pair
            if (Character.isHighSurrogate(char) && i + 1 < spacesReplaced.length) {
                // The codePointAt already handled both surrogates, so skip the next char
                continue
            }
        }
        
        // Apply lowercase using ROOT locale to avoid locale-specific issues (e.g., Turkish i)
        return result.toString().lowercase(Locale.ROOT)
    }
}
