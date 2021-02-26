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

import java.util.Optional;
import java.util.function.Function;

public class Pair<L, R> {

  private final L left;
  private final R right;

  public static <L, R> Pair<L, R> of(L left, R right) {
    return new Pair<>(left, right);
  }

  public Pair(L left, R right) {
    this.left = left;
    this.right = right;
  }

  public L getLeft() {
    return left;
  }

  public R getRight() {
    return right;
  }

  public Optional<L> getLeftOptional() {
    return Optional.ofNullable(left);
  }

  public Optional<R> getRightOptional() {
    return Optional.ofNullable(right);
  }

  public <L2, R2> Pair<L2, R2> mapPair(Function<Pair<L, R>, L2> leftMapper, Function<Pair<L, R>, R2> rightMapper) {
    return new Pair<>(leftMapper.apply(this), rightMapper.apply(this));
  }

  public <L2, R2> Pair<L2, R2> mapValues(Function<L, L2> leftMapper, Function<R, R2> rightMapper) {
    return new Pair<>(leftMapper.apply(left), rightMapper.apply(right));
  }

  public <L2> Pair<L2, R> mapLeft(Function<L, L2> leftMapper) {
    return mapValues(leftMapper, r -> r);
  }

  public <R2> Pair<L, R2> mapRight(Function<R, R2> rightMapper) {
    return mapValues(l -> l, rightMapper);
  }

  @Override
  public String toString() {
    return "Pair{" +
        "left=" + left +
        ", right=" + right +
        '}';
  }

}
