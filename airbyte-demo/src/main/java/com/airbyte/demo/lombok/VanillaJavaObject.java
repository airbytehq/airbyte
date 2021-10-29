package com.airbyte.demo.lombok;

import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VanillaJavaObject {

  private final Logger logger = LoggerFactory.getLogger(VanillaJavaObject.class);

  private final String username;
  private final String password;

  public VanillaJavaObject(final String username, final String password) {
    if (username == null) {
      throw new NullPointerException("Username shouldn't be null");
    }
    this.username = username;
    this.password = password;
  }

  @Override public String toString() {
    return "JavaObject{" +
        "username='" + username + '\'' +
        '}';
  }

  @Override public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final VanillaJavaObject that = (VanillaJavaObject) o;
    return Objects.equals(username, that.username) && Objects.equals(password, that.password);
  }

  @Override public int hashCode() {
    return Objects.hash(username, password);
  }

  public String getUsername() {
    return username;
  }

  public String getPassword() {
    return password;
  }

  public void testLog() {
    logger.error(username);
  }

  public String concat() {
    final String concat = username + ":" + password;

    return concat;
  }
}
