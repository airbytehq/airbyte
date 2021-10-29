package com.airbyte.demo.lombok;

import java.util.List;
import lombok.Builder;
import lombok.Singular;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;

@Builder(toBuilder = true)
@Slf4j
@ToString
public class LombokBuilder {

  private String username;
  private String password;
  @Builder.Default private long createdAt = System.currentTimeMillis();
  @Singular private List<String> tags;

  public static void main(final String[] args) {

    log.error(
        LombokBuilder.builder()
            .username("admin")
            .password("p@ssw0rd")
            .tag("test")
            .build()
            .toBuilder()
            .clearTags()
            .tag("Test 2")
            .toString()
    );
  }
}
