package io.airbyte.server.auth;

import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.HttpRequest;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.AbstractSecurityRule;
import io.micronaut.security.rules.SecuredAnnotationRule;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.security.rules.SecurityRuleResult;
import io.micronaut.security.token.RolesFinder;
import io.micronaut.web.router.MethodBasedRouteMatch;
import io.micronaut.web.router.RouteMatch;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Mono;

@Singleton
@Slf4j
public class CustomSecuredAnnotationRule extends SecuredAnnotationRule {

    /**
     * The order of the rule.
     */
    public static final Integer ORDER = SecuredAnnotationRule.ORDER - 100;

    /**
     *
     * @param rolesFinder Roles Parser
     */
    @Inject
    public CustomSecuredAnnotationRule(final RolesFinder rolesFinder) {
      super(rolesFinder);
    }

  /**
     * Returns {@link SecurityRuleResult#UNKNOWN} if the {@link Secured} annotation is not
     * found on the method or class, or if the route match is not method based.
     *
     * @param request The current request
     * @param routeMatch The matched route
     * @param authentication The authentication, or null if none found
     * @return The result
     */
    @Override
    public Publisher<SecurityRuleResult> check(final HttpRequest<?> request, @Nullable final RouteMatch<?> routeMatch, @Nullable final Authentication authentication) {
      log.info("Checking {} with authentication {}...", routeMatch, authentication);
      if (routeMatch instanceof MethodBasedRouteMatch) {
        final MethodBasedRouteMatch<?, ?> methodRoute = ((MethodBasedRouteMatch) routeMatch);
        log.info("Found methodRoute {}.", methodRoute);
        if (methodRoute.hasAnnotation(Secured.class)) {
          log.info("Method route {} is annotated with secured.", methodRoute);
          final Optional<String[]> optionalValue = methodRoute.getValue(Secured.class, String[].class);
          if (optionalValue.isPresent()) {
            final List<String> values = Arrays.asList(optionalValue.get());
            log.info("Found required permissions {}.", values);
            if (values.contains(SecurityRule.DENY_ALL)) {
              return Mono.just(SecurityRuleResult.REJECTED);
            }
            log.info("Comparing roles {} to user's roles {}...", values, getRoles(authentication));
            return compareRoles(values, getRoles(authentication));
          }
        }
      } else {
        log.info("Invalid route match of type {} for route match {}.", routeMatch.getClass(), routeMatch);
      }
      return Mono.just(SecurityRuleResult.UNKNOWN);
    }

    @Override
    public int getOrder() {
      return ORDER;
    }
  }
