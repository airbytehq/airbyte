package io.airbyte.oauth.google;

import io.airbyte.config.persistence.ConfigRepository;

public class GoogleAdsOauthFlow extends GoogleOAuthFlow {
  public GoogleAdsOauthFlow(ConfigRepository configRepository) {
    super(configRepository, "https://www.googleapis.com/auth/adwords");
  }
}
