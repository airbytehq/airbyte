package io.airbyte.integrations.types;

/**
 * This class used as the generic type parameter to define the type of the parameter.
 * Could be useful for specific situations when we need to have a generic type parameter
 *
 * @see io.airbyte.integrations.destination.redshift.RedshiftDestination
 */
public class GenericParamType<T> {

  private T t;

  public GenericParamType(T t) {
    this.t = t;
  }

  public void set(T t) {
    this.t = t;
  }

  public T get() {
    return t;
  }

  public static <T> GenericParamType<T> of(T t) {
    return new GenericParamType<>(t);
  }
}
