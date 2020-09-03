package io.dataline.commons.lang;

public class Container <T> {

  private final T value;

  public static <T> Container<T> of(final T value) {
    return new Container<>(value);
  }

  private Container(T value) {
    this.value = value;
  }

  public T get() {
    return value;
  }
}
