package io.airbyte.test.annotations;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/**
 * This annotation is a super set of the {@link @Test} junit annotation.
 * <p>
 * The test will only be run when the gradle integrationTest task is run
 */
@Target({ElementType.ANNOTATION_TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Test
@Tag("integration")
public @interface IntegrationTest {

}
