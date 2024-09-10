/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*
import java.util.function.Function
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Test suite for the [CursorManager] class. */
class CursorManagerTest {
    @Test
    fun testCreateCursorInfoCatalogAndStateSameCursorField() {
        val cursorManager =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actual =
            cursorManager.createCursorInfoForStream(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                StateTestConstants.getState(
                    StateTestConstants.CURSOR_FIELD1,
                    StateTestConstants.CURSOR,
                    StateTestConstants.CURSOR_RECORD_COUNT
                ),
                StateTestConstants.getStream(StateTestConstants.CURSOR_FIELD1),
                { obj: DbStreamState -> obj!!.cursor },
                { obj: DbStreamState -> obj!!.cursorField },
                CURSOR_RECORD_COUNT_FUNCTION
            )
        Assertions.assertEquals(
            CursorInfo(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.CURSOR_RECORD_COUNT,
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.CURSOR_RECORD_COUNT
            ),
            actual
        )
    }

    @Test
    fun testCreateCursorInfoCatalogAndStateSameCursorFieldButNoCursor() {
        val cursorManager =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                null,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actual =
            cursorManager.createCursorInfoForStream(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                StateTestConstants.getState(StateTestConstants.CURSOR_FIELD1, null),
                StateTestConstants.getStream(StateTestConstants.CURSOR_FIELD1),
                { obj: DbStreamState -> obj!!.cursor },
                { obj: DbStreamState -> obj!!.cursorField },
                CURSOR_RECORD_COUNT_FUNCTION
            )
        Assertions.assertEquals(
            CursorInfo(
                StateTestConstants.CURSOR_FIELD1,
                null,
                StateTestConstants.CURSOR_FIELD1,
                null
            ),
            actual
        )
    }

    @Test
    fun testCreateCursorInfoCatalogAndStateChangeInCursorFieldName() {
        val cursorManager =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actual =
            cursorManager.createCursorInfoForStream(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                StateTestConstants.getState(
                    StateTestConstants.CURSOR_FIELD1,
                    StateTestConstants.CURSOR
                ),
                StateTestConstants.getStream(StateTestConstants.CURSOR_FIELD2),
                { obj: DbStreamState -> obj!!.cursor },
                { obj: DbStreamState -> obj!!.cursorField },
                CURSOR_RECORD_COUNT_FUNCTION
            )
        Assertions.assertEquals(
            CursorInfo(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.CURSOR_FIELD2,
                null
            ),
            actual
        )
    }

    @Test
    fun testCreateCursorInfoCatalogAndNoState() {
        val cursorManager =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actual =
            cursorManager.createCursorInfoForStream(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                Optional.empty(),
                StateTestConstants.getStream(StateTestConstants.CURSOR_FIELD1),
                Function { obj: DbStreamState -> obj!!.cursor },
                Function { obj: DbStreamState -> obj!!.cursorField },
                CURSOR_RECORD_COUNT_FUNCTION
            )
        Assertions.assertEquals(
            CursorInfo(null, null, StateTestConstants.CURSOR_FIELD1, null),
            actual
        )
    }

    @Test
    fun testCreateCursorInfoStateAndNoCatalog() {
        val cursorManager =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actual =
            cursorManager.createCursorInfoForStream(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                StateTestConstants.getState(
                    StateTestConstants.CURSOR_FIELD1,
                    StateTestConstants.CURSOR
                ),
                Optional.empty(),
                { obj: DbStreamState -> obj!!.cursor },
                { obj: DbStreamState -> obj!!.cursorField },
                CURSOR_RECORD_COUNT_FUNCTION
            )
        Assertions.assertEquals(
            CursorInfo(StateTestConstants.CURSOR_FIELD1, StateTestConstants.CURSOR, null, null),
            actual
        )
    }

    // this is what full refresh looks like.
    @Test
    fun testCreateCursorInfoNoCatalogAndNoState() {
        val cursorManager =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actual =
            cursorManager.createCursorInfoForStream(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                Optional.empty(),
                Optional.empty(),
                Function { obj: DbStreamState -> obj!!.cursor },
                Function { obj: DbStreamState -> obj!!.cursorField },
                CURSOR_RECORD_COUNT_FUNCTION
            )
        Assertions.assertEquals(CursorInfo(null, null, null, null), actual)
    }

    @Test
    fun testCreateCursorInfoStateAndCatalogButNoCursorField() {
        val cursorManager =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actual =
            cursorManager.createCursorInfoForStream(
                StateTestConstants.NAME_NAMESPACE_PAIR1,
                StateTestConstants.getState(
                    StateTestConstants.CURSOR_FIELD1,
                    StateTestConstants.CURSOR
                ),
                StateTestConstants.getStream(null),
                { obj: DbStreamState -> obj!!.cursor },
                { obj: DbStreamState -> obj!!.cursorField },
                CURSOR_RECORD_COUNT_FUNCTION
            )
        Assertions.assertEquals(
            CursorInfo(StateTestConstants.CURSOR_FIELD1, StateTestConstants.CURSOR, null, null),
            actual
        )
    }

    @Test
    fun testGetters() {
        val cursorManager: CursorManager<*> =
            createCursorManager(
                StateTestConstants.CURSOR_FIELD1,
                StateTestConstants.CURSOR,
                StateTestConstants.NAME_NAMESPACE_PAIR1
            )
        val actualCursorInfo =
            CursorInfo(StateTestConstants.CURSOR_FIELD1, StateTestConstants.CURSOR, null, null)

        Assertions.assertEquals(
            Optional.of(actualCursorInfo),
            cursorManager.getCursorInfo(StateTestConstants.NAME_NAMESPACE_PAIR1)
        )
        Assertions.assertEquals(
            Optional.empty<Any>(),
            cursorManager.getCursorField(StateTestConstants.NAME_NAMESPACE_PAIR1)
        )
        Assertions.assertEquals(
            Optional.empty<Any>(),
            cursorManager.getCursor(StateTestConstants.NAME_NAMESPACE_PAIR1)
        )

        Assertions.assertEquals(
            Optional.empty<Any>(),
            cursorManager.getCursorInfo(StateTestConstants.NAME_NAMESPACE_PAIR2)
        )
        Assertions.assertEquals(
            Optional.empty<Any>(),
            cursorManager.getCursorField(StateTestConstants.NAME_NAMESPACE_PAIR2)
        )
        Assertions.assertEquals(
            Optional.empty<Any>(),
            cursorManager.getCursor(StateTestConstants.NAME_NAMESPACE_PAIR2)
        )
    }

    private fun createCursorManager(
        cursorField: String?,
        cursor: String?,
        nameNamespacePair: AirbyteStreamNameNamespacePair?
    ): CursorManager<DbStreamState> {
        val dbStreamState = StateTestConstants.getState(cursorField, cursor).get()
        return CursorManager(
            StateTestConstants.getCatalog(cursorField).orElse(null),
            { setOf(dbStreamState) },
            { obj: DbStreamState -> obj!!.cursor },
            { obj: DbStreamState -> obj!!.cursorField },
            CURSOR_RECORD_COUNT_FUNCTION,
            { nameNamespacePair },
            false
        )
    }

    companion object {
        private val CURSOR_RECORD_COUNT_FUNCTION = Function { stream: DbStreamState ->
            if (stream.cursorRecordCount != null) {
                return@Function stream.cursorRecordCount
            } else {
                return@Function 0L
            }
        }
    }
}
