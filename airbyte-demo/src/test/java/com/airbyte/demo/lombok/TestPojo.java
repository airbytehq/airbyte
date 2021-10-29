package com.airbyte.demo.lombok;

import com.google.common.collect.Lists;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class TestPojo {

  private final static String USERNAME = "admin";
  private final static String PASSWORD = "p@ssw0rd";

  @Test
  public void testJunit() {
    final LombokObject lombokObject = new LombokObject(USERNAME, PASSWORD);
    final VanillaJavaObject vanillaJavaObject = new VanillaJavaObject(USERNAME, PASSWORD);

    Assertions.assertEquals(lombokObject.getUsername(), vanillaJavaObject.getUsername());
    Assertions.assertTrue(lombokObject.concat().startsWith(USERNAME));
    Assertions.assertTrue(lombokObject.concat().endsWith(PASSWORD));

    final NullPointerException exception = Assertions.assertThrows(NullPointerException.class,
        () -> new VanillaJavaObject(null, null),
        "Username shouldn't be null"
    );

    Assertions.assertTrue(exception.getCause() == null);
  }

  @Test
  public void testAssertJ() {
    final LombokObject lombokObject = new LombokObject(USERNAME, PASSWORD);
    final VanillaJavaObject vanillaJavaObject = new VanillaJavaObject(USERNAME, PASSWORD);

    org.assertj.core.api.Assertions.assertThat(lombokObject.getUsername()).isEqualTo(vanillaJavaObject.getUsername());
    org.assertj.core.api.Assertions.assertThat(lombokObject.concat())
        .startsWith(USERNAME)
        .endsWith(PASSWORD);

    org.assertj.core.api.Assertions.assertThatThrownBy(
            () -> new LombokObject(null, null)
        ).isInstanceOf(NullPointerException.class)
        .hasMessageContaining("username")
        .hasNoCause();
  }

  @Test
  public void otherAssertJBenefits() {
    // final Optional<String> strOpt = Optional.empty();
    final Optional<String> strOpt = Optional.of("strOpt");

    org.assertj.core.api.Assertions.assertThat(strOpt)
        .isNotEmpty()
        .contains("strOpt");

    final List<String> strings = Lists.newArrayList("one", "three", "two");
    org.assertj.core.api.Assertions.assertThat(strings)
        .hasSize(3)
        .containsExactlyInAnyOrder("one", "two", "three")
        .containsExactly("one", "three", "two")
        .containsExactly("one", "two", "three");

    final Map<Integer, String> map = new HashMap() {{
      put(1, "one");
      put(2, "two");
      put(3, "three");
    }};
    org.assertj.core.api.Assertions.assertThat(map)
        .doesNotContainKey(4)
        .doesNotContainValue("four");
  }
}
