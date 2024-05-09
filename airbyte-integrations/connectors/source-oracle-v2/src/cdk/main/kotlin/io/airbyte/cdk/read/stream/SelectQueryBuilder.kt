/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.read.CdcNonResumableInitialSyncStarting
import io.airbyte.cdk.read.CdcResumableInitialSyncOngoing
import io.airbyte.cdk.read.CdcResumableInitialSyncStarting
import io.airbyte.cdk.read.CursorBasedIncrementalOngoing
import io.airbyte.cdk.read.CursorBasedNonResumableInitialSyncStarting
import io.airbyte.cdk.read.CursorBasedResumableInitialSyncOngoing
import io.airbyte.cdk.read.CursorBasedResumableInitialSyncStarting
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.FullRefreshNonResumableStarting
import io.airbyte.cdk.read.FullRefreshResumableOngoing
import io.airbyte.cdk.read.FullRefreshResumableStarting
import io.airbyte.cdk.read.NonResumableBackfillState
import io.airbyte.cdk.read.ResumableSelectState

object SelectQueryBuilder {

    fun selectMaxCursorValue(table: TableName, cursorColumn: Field): SelectQueryRootNode =
        SelectQueryRootNode(
                SelectColumnMaxValue(cursorColumn),
                From(table),
                NoWhere,
                NoOrderBy,
                NoLimit
            )
            .optimize()

    fun selectData(state: NonResumableBackfillState): SelectQueryRootNode = state.ast().optimize()

    fun selectData(state: ResumableSelectState): SelectQueryRootNode = state.ast().optimize()

    private fun NonResumableBackfillState.ast(): SelectQueryRootNode =
        SelectQueryRootNode(
            SelectColumns(key.fields),
            From(key.table),
            when (this) {
                is FullRefreshNonResumableStarting -> NoWhere
                is CdcNonResumableInitialSyncStarting -> NoWhere
                is CursorBasedNonResumableInitialSyncStarting ->
                    Where(LesserOrEqual(cursor, cursorCheckpoint))
            },
            NoOrderBy,
            NoLimit,
        )

    private fun ResumableSelectState.ast(): SelectQueryRootNode {
        val extraColumnCandidates: List<Field> =
            when (this) {
                is CdcResumableInitialSyncStarting -> primaryKey
                is CdcResumableInitialSyncOngoing -> primaryKey
                is CursorBasedResumableInitialSyncStarting -> primaryKey
                is CursorBasedResumableInitialSyncOngoing -> primaryKey
                is CursorBasedIncrementalOngoing -> listOf(cursor)
                is FullRefreshResumableStarting -> primaryKey
                is FullRefreshResumableOngoing -> primaryKey
            }
        val where: WhereNode =
            when (this) {
                is CdcResumableInitialSyncStarting -> NoWhere
                is CdcResumableInitialSyncOngoing ->
                    Where(pkClause(primaryKey, primaryKeyCheckpoint))
                is CursorBasedResumableInitialSyncStarting ->
                    Where(LesserOrEqual(cursor, cursorCheckpoint))
                is CursorBasedResumableInitialSyncOngoing -> {
                    val pk = pkClause(primaryKey, primaryKeyCheckpoint)
                    val leq = LesserOrEqual(cursor, cursorCheckpoint)
                    Where(And(listOf(pk, leq)))
                }
                is CursorBasedIncrementalOngoing -> {
                    val gt = Greater(cursor, cursorCheckpoint)
                    val leq = LesserOrEqual(cursor, cursorTarget)
                    Where(And(listOf(gt, leq)))
                }
                is FullRefreshResumableStarting -> NoWhere
                is FullRefreshResumableOngoing -> Where(pkClause(primaryKey, primaryKeyCheckpoint))
            }

        return SelectQueryRootNode(
            SelectColumns(key.fields + extraColumnCandidates),
            From(key.table),
            where,
            OrderBy(extraColumnCandidates),
            Limit(limit)
        )
    }

    private fun pkClause(pkCols: List<Field>, pkValues: List<JsonNode>): WhereClauseNode {
        val zipped: List<Pair<Field, JsonNode>> = pkCols.zip(pkValues)
        val disj: List<And> =
            zipped.mapIndexed { idx: Int, (gtCol: Field, gtValue: JsonNode) ->
                val eqs =
                    zipped.take(idx).map { (eqCol: Field, eqValue: JsonNode) ->
                        Equal(eqCol, eqValue)
                    }
                And(eqs + listOf(Greater(gtCol, gtValue)))
            }
        return Or(disj)
    }
}
