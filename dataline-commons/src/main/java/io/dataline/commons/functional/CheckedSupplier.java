package io.dataline.commons.functional;

@FunctionalInterface
public interface CheckedSupplier<T, E extends Throwable> {

  T get() throws E;

}
