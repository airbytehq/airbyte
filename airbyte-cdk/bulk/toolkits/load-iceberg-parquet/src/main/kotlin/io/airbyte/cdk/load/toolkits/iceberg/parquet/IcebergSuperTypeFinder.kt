/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet

import io.airbyte.cdk.ConfigErrorException
import jakarta.inject.Singleton
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Type.PrimitiveType
import org.apache.iceberg.types.Type.TypeID
import org.apache.iceberg.types.Type.TypeID.*
import org.apache.iceberg.types.TypeUtil
import org.apache.iceberg.types.Types.*

/**
 * A utility class that determines a "supertype" given two Iceberg [Type]s.
 *
 * The "supertype" is a type to which both input types can safely be promoted without data loss. For
 * instance, INT can be promoted to LONG, FLOAT can be promoted to DOUBLE, etc.
 *
 * @property IcebergTypesComparator comparator used to verify deep type equality.
 */
@Singleton
class IcebergSuperTypeFinder(private val icebergTypesComparator: IcebergTypesComparator) {
    private val unsupportedTypeIds = setOf(BINARY, DECIMAL, FIXED, UUID, MAP, TIMESTAMP_NANO)

    /**
     * Returns a supertype for [existingType] and [incomingType] if one exists.
     * - If they are deeply equal (according to [IcebergTypesComparator.typesAreEqual]), returns the
     * [existingType] as-is.
     * - Otherwise, attempts to combine them into a valid supertype.
     * - Throws [ConfigErrorException] if no valid supertype can be found.
     */
    fun findSuperType(existingType: Type, incomingType: Type, columnName: String): Type {
        // If the two types are already deeply equal, return one of them (arbitrary).
        if (icebergTypesComparator.typesAreEqual(incomingType, existingType)) {
            return existingType
        }
        // Otherwise, attempt to combine them into a valid supertype.
        return combineTypes(existingType, incomingType, columnName)
    }

    /**
     * Combines two top-level [Type]s. If exactly one is primitive and the other is non-primitive,
     * no supertype is possible => throws [ConfigErrorException].
     */
    private fun combineTypes(existingType: Type, incomingType: Type, columnName: String): Type {
        if (existingType.isPrimitiveType != incomingType.isPrimitiveType) {
            throwIllegalTypeCombination(existingType, incomingType, columnName)
        }

        // Both are primitive
        if (existingType.isPrimitiveType && incomingType.isPrimitiveType) {
            return combinePrimitives(
                existingType.asPrimitiveType(),
                incomingType.asPrimitiveType(),
                columnName
            )
        }

        // Both are non-primitive => not currently supported
        throwIllegalTypeCombination(existingType, incomingType, columnName)
    }

    /**
     * Checks whether either type is unsupported or unmapped (e.g. BINARY, DECIMAL, FIXED, etc.).
     *
     * @throws ConfigErrorException if either type is unsupported.
     */
    private fun validateTypeIds(typeId1: TypeID, typeId2: TypeID) {
        val providedTypes = listOf(typeId1, typeId2)
        val foundUnsupported = providedTypes.filter { it in unsupportedTypeIds }

        if (foundUnsupported.isNotEmpty()) {
            throw IllegalArgumentException(
                "Unsupported or unmapped Iceberg type(s): ${foundUnsupported.joinToString()}. Please implement handling if needed."
            )
        }
    }

    /**
     * Attempts to combine two [PrimitiveType]s into a valid supertype by using
     * [TypeUtil.isPromotionAllowed].
     *
     * - If they have the same [TypeID], just returns the existing type (since they’re not deeply
     * equal, but the top-level ID is the same. You may want to consider e.g. TIMESTAMP with/without
     * UTC).
     * - If they have different IDs, tries known promotions (INT->LONG, FLOAT->DOUBLE).
     * - If promotion is not allowed, throws [ConfigErrorException].
     */
    private fun combinePrimitives(
        existingType: PrimitiveType,
        incomingType: PrimitiveType,
        columnName: String
    ): Type {
        val existingTypeId = existingType.typeId()
        val incomingTypeId = incomingType.typeId()
        // If promotion is not allowed by Iceberg, fail fast.
        if (!TypeUtil.isPromotionAllowed(existingType, incomingType)) {
            throwIllegalTypeCombination(existingType, incomingType, columnName)
        }

        validateTypeIds(existingTypeId, incomingTypeId)

        // If both are the same type ID, we just use the existing type
        if (existingTypeId == incomingTypeId) {
            // For timestamps, you'd want to reconcile UTC. This is simplified here.
            return existingType
        }

        // Otherwise, we attempt known promotions
        return when (existingTypeId) {
            INTEGER ->
                when (incomingTypeId) {
                    LONG -> LongType.get()
                    else -> throwIllegalTypeCombination(existingType, incomingType, columnName)
                }
            FLOAT ->
                when (incomingTypeId) {
                    DOUBLE -> DoubleType.get()
                    else -> throwIllegalTypeCombination(existingType, incomingType, columnName)
                }
            else -> throwIllegalTypeCombination(existingType, incomingType, columnName)
        }
    }

    /** Helper function to throw a standardized [ConfigErrorException] for invalid type combos. */
    private fun throwIllegalTypeCombination(
        existingType: Type,
        incomingType: Type,
        columnName: String
    ): Nothing =
        throw ConfigErrorException(
            "Schema evolution for column \"$columnName\" between $existingType and $incomingType is not allowed."
        )
}
