package io.airbyte.cdk.initialization

import io.micronaut.context.annotation.Bean
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Test


@MicronautTest
class TestApplicationYaml {
    @Inject lateinit var testBean: TestBean

    @Test
    fun testApplicationYamlInjection() {
        assert(testBean.testApplicationYamlEntry == "value")
    }
}

data class TestBean(val testApplicationYamlEntry: String)
@Factory
class TestFactory {
    @Bean
    fun testBean(@Value("\${airbyte.test}") testValue: String): TestBean {
        return TestBean(testValue)
    }
}
