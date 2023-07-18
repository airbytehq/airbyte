/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import java.util.LinkedList;
import java.util.List;

public class TreeNode<T> {

  private T data;
  private TreeNode<T> parent;
  private List<TreeNode<T>> children;

  public TreeNode(final T data) {
    this.data = data;
    this.children = new LinkedList<>();
  }

  public TreeNode<T> addChild(final T child) {
    final TreeNode<T> childNode = new TreeNode<T>(child);
    childNode.parent = this;
    this.children.add(childNode);
    return childNode;
  }

  public boolean hasChildren() {
    return children != null && !children.isEmpty();
  }

  public T getData() {
    return data;
  }

  public void setData(final T data) {
    this.data = data;
  }

  public TreeNode<T> getParent() {
    return parent;
  }

  public void setParent(final TreeNode<T> parent) {
    this.parent = parent;
  }

  public List<TreeNode<T>> getChildren() {
    return children;
  }

  public void setChildren(final List<TreeNode<T>> children) {
    this.children = children;
  }

}
