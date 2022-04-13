/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.sources;

import io.micronaut.context.env.KubernetesEnvironmentPropertySource;
import io.micronaut.context.env.PropertySource;
import io.micronaut.management.endpoint.info.InfoSource;
import javax.inject.Singleton;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Flux;

@Singleton
public class AirbyteServerInfoSource implements InfoSource {

  @Override
  public Publisher<PropertySource> getSource() {
    return Flux.just(new KubernetesEnvironmentPropertySource());
  }

}
