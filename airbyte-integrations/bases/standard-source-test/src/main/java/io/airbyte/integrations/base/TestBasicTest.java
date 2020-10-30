package io.airbyte.integrations.base;

import static org.junit.jupiter.api.Assertions.fail;

import org.junit.jupiter.api.Test;

public class TestBasicTest {

  @Test
  void myTest(){
    System.out.println("true = " + true);
  }

  @Test
  void myTest2(){
    fail();
  }
}
