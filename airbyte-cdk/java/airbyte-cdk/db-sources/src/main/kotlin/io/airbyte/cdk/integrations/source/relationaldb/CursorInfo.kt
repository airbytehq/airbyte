/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import java.util.*

class CursorInfo(
    val originalCursorField: String?,
    val originalCursor: String?,
    val originalCursorRecordCount: Long,
    val cursorField: String?,
    var cursor: String?,
    var cursorRecordCount: Long
) {
    constructor(
        originalCursorField: String?,
        originalCursor: String?,
        cursorField: String?,
        cursor: String?
    ) : this(originalCursorField, originalCursor, 0L, cursorField, cursor, 0L)

    fun setCursor(cursor: String?): CursorInfo {
        this.cursor = cursor
        return this
    }

    fun setCursorRecordCount(cursorRecordCount: Long): CursorInfo {
        this.cursorRecordCount = cursorRecordCount
        return this
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as CursorInfo
        return originalCursorField == that.originalCursorField &&
            originalCursor == that.originalCursor &&
            originalCursorRecordCount == that.originalCursorRecordCount &&
            cursorField == that.cursorField &&
            cursor == that.cursor &&
            cursorRecordCount == that.cursorRecordCount
    }

    override fun hashCode(): Int {
        return Objects.hash(
            originalCursorField,
            originalCursor,
            originalCursorRecordCount,
            cursorField,
            cursor,
            cursorRecordCount
        )
    }

    override fun toString(): String {
        return "CursorInfo{" +
            "originalCursorField='" +
            originalCursorField +
            '\'' +
            ", originalCursor='" +
            originalCursor +
            '\'' +
            ", originalCursorRecordCount='" +
            originalCursorRecordCount +
            '\'' +
            ", cursorField='" +
            cursorField +
            '\'' +
            ", cursor='" +
            cursor +
            '\'' +
            ", cursorRecordCount='" +
            cursorRecordCount +
            '\'' +
            '}'
    }
}
