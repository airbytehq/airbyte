package io.airbyte.server.auth;

import io.micronaut.security.rules.SecuredAnnotationRule;
import io.micronaut.security.token.RolesFinder;
import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class CustomSecuredAnnotationRule extends SecuredAnnotationRule {

  /**
   * The order of the rule.
   */
  public static final Integer ORDER = SecuredAnnotationRule.ORDER - 100;

  public CustomSecuredAnnotationRule(final RolesFinder rolesFinder) {
    super(rolesFinder);
  }

  @Override
  public int getOrder() {
      return ORDER;
    }
}