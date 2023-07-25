package io.airbyte.cdk;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Disabled;


class CDKConstantsTest {

    /* TODO: Remove these three canary tests once real tests are in place. */
    @Test
    void getVersion() {
        System.out.println("Running getVersion test");
        assertEquals("0.0.1-SNAPSHOT", CDKConstants.VERSION);
    }

    @Test
    void mustPass() {
        assertTrue(true, "This should always pass.");
    }

    @Test
    // Comment out this line to force failure:
    @Disabled("This is an intentionally failing test (skipped).")
    void mustFail() {
        assertTrue(false, "This is an intentionally failing test.");
    }
}
