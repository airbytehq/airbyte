package io.airbyte.integrations.source.postgres.ctid;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import io.airbyte.integrations.source.postgres.ctid.PostgresCtidHandler.Ctid;
import org.junit.jupiter.api.Test;

public class PostgresCtidHandlerTest {

  @Test
  void testCtidQueryBounds() {
    var chunks = PostgresCtidHandler.ctidQueryPlan(new Ctid(0,0),380545032192L, 8192L, 2);
    assertNotNull(chunks);
    chunks = PostgresCtidHandler.ctidQueryPlan(new Ctid("(23000000,123)"),380545032192L, 8192L, 2);
    assertNotNull(chunks);
  }
}
