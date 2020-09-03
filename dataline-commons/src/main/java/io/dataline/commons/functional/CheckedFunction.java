package io.dataline.commons.functional;

@FunctionalInterface
public interface CheckedFunction<T, R, E extends Throwable> {

  R apply(T t) throws E;

  static <T, E extends Throwable> CheckedFunction<T, T, E> identity() {
    return e -> e;
  }

}
