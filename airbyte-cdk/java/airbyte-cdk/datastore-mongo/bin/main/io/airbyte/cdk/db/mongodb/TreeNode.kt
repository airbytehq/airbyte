/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.mongodb

import java.util.*

class TreeNode<T>(var data: T) {
    var parent: TreeNode<T>? = null
    var children: MutableList<TreeNode<T>>?

    init {
        this.children = LinkedList()
    }

    fun addChild(child: T): TreeNode<T> {
        val childNode = TreeNode(child)
        childNode.parent = this
        children!!.add(childNode)
        return childNode
    }

    fun hasChildren(): Boolean {
        return children != null && !children!!.isEmpty()
    }
}
