package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

import java.time.Duration;

public class ElasticsearchConnectionTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(ElasticsearchConnectionTest.class);

    private ObjectMapper mapper = new ObjectMapper();
    //private JsonNode configJson;
    private ElasticsearchContainer container;

    @BeforeEach
    public void beforeAll() {
        container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.12.1")
                .withEnv("ES_JAVA_OPTS", "-Xms512m -Xmx512m")
                .withStartupTimeout(Duration.ofSeconds(90));
        container.start();

    }

    @AfterEach
    public void afterAll() {
        container.stop();
        container.close();
    }

    public void e2e() {

    }
}
