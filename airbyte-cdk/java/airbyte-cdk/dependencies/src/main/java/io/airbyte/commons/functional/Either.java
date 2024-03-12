/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import java.util.Objects;

/**
 * A class that represents a value of one of two possible types (a disjoint union). An instance of
 * Either is an instance of Left or Right.
 *
 * A common use of Either is for error handling in functional programming. By convention, Left is
 * failure and Right is success.
 *
 * @param <Error> the type of the left value
 * @param <Result> the type of the right value
 */
public class Either<Error, Result> {

  private final Error left;
  private final Result right;

  private Either(Error left, Result right) {
    this.left = left;
    this.right = right;
  }

  public boolean isLeft() {
    return left != null;
  }

  public boolean isRight() {
    return right != null;
  }

  public Error getLeft() {
    return left;
  }

  public Result getRight() {
    return right;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Either<?, ?> either = (Either<?, ?>) o;
    return Objects.equals(left, either.left) && Objects.equals(right, either.right);
  }

  @Override
  public int hashCode() {
    return Objects.hash(left, right);
  }

  public static <Error, Result> Either<Error, Result> left(Error error) {
    return new Either<>(error, null);
  }

  public static <Error, Result> Either<Error, Result> right(Result result) {
    return new Either<>(null, result);
  }

}
