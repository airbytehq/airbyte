package io.airbyte.oauth.google;

import io.airbyte.config.persistence.ConfigRepository;

public class GoogleAnalyticsOauthFlow extends GoogleOAuthFlow {

  public GoogleAnalyticsOauthFlow(ConfigRepository configRepository) {
    super(configRepository, "https%3A//www.googleapis.com/auth/analytics.readonly");
  }
}
