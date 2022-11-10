package io.airbyte.api.server.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class AirbyteAccessToken {

  public static final String SUBJECT = "sub";
  public static final String EMAIL = "email";
  public static final String EMAIL_VERIFIED = "email_verified";
  public static final String USER_ID = "user_id";

  @JsonProperty(SUBJECT)
  private String subject;
  private String email;

  @JsonProperty(EMAIL_VERIFIED)
  private String emailVerified;

  public String getEmailVerified() {
    return emailVerified;
  }

  public void setEmailVerified(String emailVerified) {
    this.emailVerified = emailVerified;
  }

  public String getEmail() {
    return email;
  }

  public void setEmail(String email) {
    this.email = email;
  }

  public String getSubject() {
    return subject;
  }

  public void setSubject(String subject) {
    this.subject = subject;
  }
}
