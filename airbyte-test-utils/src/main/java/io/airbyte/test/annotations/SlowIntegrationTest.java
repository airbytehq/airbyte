/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.annotations;

import java.lang.annotation.ElementType;
import java.lang.annotation.Target;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/**
 * This annotation is a super set of the {@link Test} junit annotation.
 * <p>
 * The test will only be run when the gradle slowIntegrationTests task is run
 */
@Target({ElementType.ANNOTATION_TYPE, ElementType.TYPE})
@Tag("platform-slow-integration")
public @interface SlowIntegrationTest {

}
