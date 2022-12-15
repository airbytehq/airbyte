/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import java.util.LinkedList;
import java.util.List;

public class TreeNode<T> {

  private T data;
  private TreeNode<T> parent;
  private List<TreeNode<T>> children;

  public TreeNode(T data) {
    this.data = data;
    this.children = new LinkedList<>();
  }

  public TreeNode<T> addChild(T child) {
    TreeNode<T> childNode = new TreeNode<T>(child);
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

  public void setData(T data) {
    this.data = data;
  }

  public TreeNode<T> getParent() {
    return parent;
  }

  public void setParent(TreeNode<T> parent) {
    this.parent = parent;
  }

  public List<TreeNode<T>> getChildren() {
    return children;
  }

  public void setChildren(List<TreeNode<T>> children) {
    this.children = children;
  }

}
