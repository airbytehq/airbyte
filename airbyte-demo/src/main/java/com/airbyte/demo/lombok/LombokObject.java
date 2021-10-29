package com.airbyte.demo.lombok;

import lombok.Getter;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;
import lombok.val;

@RequiredArgsConstructor
@ToString
@Getter
@Slf4j
public class LombokObject {

  @NonNull private final String username;
  @ToString.Exclude private final String password;

  public void testLog() {
    log.error(username);
  }

  public String concat() {
    val concat = username + ":" + password;

    return concat;
  }
}
