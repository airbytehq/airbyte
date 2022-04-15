package io.airbyte.integrations.types;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class GenericParamTypeTest {

  private GenericParamType<String> genericParamType;

  @BeforeEach
  void setUp() {
    genericParamType = new GenericParamType("sd");
  }

  @Test
  public void testGet() {
    String result = genericParamType.get();
    assertEquals("sd", result);
  }

  @Test
  public void testOf() {
    GenericParamType<String> genericParamType = GenericParamType.of("sd");
    assertEquals("sd", genericParamType.get());
  }

  @Test
  public void testSet() {
    genericParamType.set("test");
    assertEquals("java.lang.String", genericParamType.get().getClass().getName());
    assertEquals("test", genericParamType.get());
  }
}