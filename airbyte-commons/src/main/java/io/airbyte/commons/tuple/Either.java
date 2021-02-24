/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.commons.tuple;

import com.google.common.base.Preconditions;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;

public class Either<L, R> {

  private final L left;
  private final R right;

  public static <L, R> Either<L, R> left(L left) {
    return new Either<>(left, null);
  }

  public static <L, R> Either<L, R> right(R right) {
    return new Either<>(null, right);
  }

  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  public static <L, R> Either<L, R> from(Optional<L> left, Optional<R> right) {
    Preconditions.checkArgument(left.isPresent() ^ right.isPresent());
    return new Either<>(left.orElse(null), right.orElse(null));
  }

  public static <L, R> Either<L, R> from(L left, R right) {
    return new Either<>(left, right);
  }

  public static <L, R> Either<L, R> fromPair(Pair<L, R> pair, Predicate<Pair<L, R>> pairPredicate) {
    if (pairPredicate.test(pair)) {
      return Either.left(pair.getLeft());
    } else {
      return Either.right(pair.getRight());
    }
  }

  public Either(L left, R right) {
    Preconditions.checkArgument(null != left ^ null != right);
    this.left = left;
    this.right = right;
  }

  public boolean hasLeft() {
    return null != left;
  }

  public boolean hasRight() {
    return null != right;
  }

  public Optional<L> getLeft() {
    return Optional.ofNullable(left);
  }

  public Optional<R> getRight() {
    return Optional.ofNullable(right);
  }

  public <L2> Either<L2, R> mapLeft(Function<Optional<L>, L2> leftMapper) {
    return new Either<>(leftMapper.apply(Optional.ofNullable(left)), right);
  }

  public <R2> Either<L, R2> mapRight(Function<Optional<R>, R2> rightMapper) {
    return new Either<>(left, rightMapper.apply(Optional.ofNullable(right)));
  }

  public <T> T map(Function<L, T> leftMapper, Function<R, T> rightMapper) {
    if (hasLeft()) {
      return leftMapper.apply(left);
    } else {
      return rightMapper.apply(right);
    }
  }

  public void map(Consumer<L> leftConsumer, Consumer<R> rightConsumer) {
    if (hasLeft()) {
      leftConsumer.accept(left);
    } else {
      rightConsumer.accept(right);
    }
  }

  @Override
  public String toString() {
    return "Either{" +
        "left=" + left +
        ", right=" + right +
        '}';
  }

}
