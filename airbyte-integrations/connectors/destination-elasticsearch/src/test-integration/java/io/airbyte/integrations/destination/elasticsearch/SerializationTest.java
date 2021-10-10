/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import java.time.Duration;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

public class SerializationTest {

  @BeforeAll
  public static void setup() {
    ElasticsearchContainer container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.12.1")
        .withEnv("ES_JAVA_OPTS", "-Xms256m -Xmx256m")
        .withStartupTimeout(Duration.ofSeconds(30));
    container.start();

  }

  @Test
  public void test() {

  }

}
