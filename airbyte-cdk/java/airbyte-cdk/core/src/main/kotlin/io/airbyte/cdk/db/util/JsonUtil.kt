/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.util

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ContainerNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.math.BigDecimal

object JsonUtil {
    private const val ERROR_MESSAGE = "Can't populate the node type : "

    @JvmStatic
    fun putBooleanValueIntoJson(node: ContainerNode<*>, value: Boolean, fieldName: String?) {
        if (node is ArrayNode) {
            node.add(value)
        } else if (node is ObjectNode) {
            node.put(fieldName, value)
        } else {
            throw RuntimeException(ERROR_MESSAGE + node.javaClass.name)
        }
    }

    @JvmStatic
    fun putLongValueIntoJson(node: ContainerNode<*>, value: Long, fieldName: String?) {
        if (node is ArrayNode) {
            node.add(value)
        } else if (node is ObjectNode) {
            node.put(fieldName, value)
        } else {
            throw RuntimeException(ERROR_MESSAGE + node.javaClass.name)
        }
    }

    @JvmStatic
    fun putDoubleValueIntoJson(node: ContainerNode<*>, value: Double, fieldName: String?) {
        if (node is ArrayNode) {
            node.add(value)
        } else if (node is ObjectNode) {
            node.put(fieldName, value)
        } else {
            throw RuntimeException(ERROR_MESSAGE + node.javaClass.name)
        }
    }

    @JvmStatic
    fun putBigDecimalValueIntoJson(node: ContainerNode<*>, value: BigDecimal?, fieldName: String?) {
        if (node is ArrayNode) {
            node.add(value)
        } else if (node is ObjectNode) {
            node.put(fieldName, value)
        } else {
            throw RuntimeException(ERROR_MESSAGE + node.javaClass.name)
        }
    }

    @JvmStatic
    fun putStringValueIntoJson(node: ContainerNode<*>, value: String?, fieldName: String?) {
        if (node is ArrayNode) {
            node.add(value)
        } else if (node is ObjectNode) {
            node.put(fieldName, value)
        } else {
            throw RuntimeException(ERROR_MESSAGE + node.javaClass.name)
        }
    }

    @JvmStatic
    fun putBytesValueIntoJson(node: ContainerNode<*>, value: ByteArray?, fieldName: String?) {
        if (node is ArrayNode) {
            node.add(value)
        } else if (node is ObjectNode) {
            node.put(fieldName, value)
        } else {
            throw RuntimeException(ERROR_MESSAGE + node.javaClass.name)
        }
    }
}
