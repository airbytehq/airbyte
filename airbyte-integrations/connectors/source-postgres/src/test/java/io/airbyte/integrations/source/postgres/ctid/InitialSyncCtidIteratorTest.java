/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.EIGHT_KB;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.GIGABYTE;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.jupiter.api.Test;

public class InitialSyncCtidIteratorTest {

  @Test
  void testCtidQueryBounds() {
    var chunks = InitialSyncCtidIterator.ctidQueryPlan(Ctid.ZERO, 380545032192L, 8192L, 50, GIGABYTE);
    var expected = List.of(
        Pair.of(Ctid.ZERO, Ctid.of(6553600, 0)),
        Pair.of(Ctid.of(6553600, 0), Ctid.of(13107200, 0)),
        Pair.of(Ctid.of(13107200, 0), Ctid.of(19660800, 0)),
        Pair.of(Ctid.of(19660800, 0), Ctid.of(26214400, 0)),
        Pair.of(Ctid.of(26214400, 0), Ctid.of(32768000, 0)),
        Pair.of(Ctid.of(32768000, 0), Ctid.of(39321600, 0)),
        Pair.of(Ctid.of(39321600, 0), Ctid.of(45875200, 0)),
        Pair.of(Ctid.of(45875200, 0), null));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidQueryPlan(new Ctid("(23000000,123)"), 380545032192L, 8192L, 45, GIGABYTE);
    expected = List.of(
        Pair.of(Ctid.of("(23000000,123)"), Ctid.of(28898240, 0)),
        Pair.of(Ctid.of(28898240, 0), Ctid.of("(34796480,0)")),
        Pair.of(Ctid.of("(34796480,0)"), Ctid.of(40694720, 0)),
        Pair.of(Ctid.of(40694720, 0), null));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidQueryPlan(Ctid.of(0, 0), 380545L, 8192L, 45, GIGABYTE);
    expected = List.of(Pair.of(Ctid.ZERO, null));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidQueryPlan(Ctid.of(9876, 5432), 380545L, 8192L, 45, GIGABYTE);
    expected = List.of(
        Pair.of(Ctid.of(9876, 5432), null));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidQueryPlan(Ctid.ZERO, 4096L, 8192L, 45, GIGABYTE);
    expected = List.of(
        Pair.of(Ctid.ZERO, null));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidQueryPlan(Ctid.of(8, 1), 819200L, 81920L, 50, EIGHT_KB);
    expected = List.of(Pair.of(Ctid.of(8, 1), Ctid.of(9, 0)), Pair.of(Ctid.of(9, 0), Ctid.of(10, 0)));
    assertEquals(expected, chunks);
  }

  @Test
  void testLegacyCtidQueryBounds() {
    var chunks = InitialSyncCtidIterator.ctidLegacyQueryPlan(Ctid.of(0, 184), 3805450321L, 8192L, 50, GIGABYTE, 185);
    var expected = List.of(
        Pair.of(Ctid.of(0, 185), Ctid.of(27027, 185)),
        Pair.of(Ctid.of(27028, 1), Ctid.of(54054, 185)),
        Pair.of(Ctid.of(54055, 1), Ctid.of(81081, 185)),
        Pair.of(Ctid.of(81082, 1), Ctid.of(108108, 185)),
        Pair.of(Ctid.of(108109, 1), Ctid.of(135135, 185)),
        Pair.of(Ctid.of(135136, 1), Ctid.of(162162, 185)),
        Pair.of(Ctid.of(162163, 1), Ctid.of(189189, 185)),
        Pair.of(Ctid.of(189190, 1), Ctid.of(216216, 185)),
        Pair.of(Ctid.of(216217, 1), Ctid.of(243243, 185)),
        Pair.of(Ctid.of(243244, 1), Ctid.of(270270, 185)),
        Pair.of(Ctid.of(270271, 1), Ctid.of(297297, 185)),
        Pair.of(Ctid.of(297298, 1), Ctid.of(324324, 185)),
        Pair.of(Ctid.of(324325, 1), Ctid.of(351351, 185)),
        Pair.of(Ctid.of(351352, 1), Ctid.of(378378, 185)),
        Pair.of(Ctid.of(378379, 1), Ctid.of(405405, 185)),
        Pair.of(Ctid.of(405406, 1), Ctid.of(432432, 185)),
        Pair.of(Ctid.of(432433, 1), Ctid.of(459459, 185)),
        Pair.of(Ctid.of(459460, 1), Ctid.of(486486, 185)),
        Pair.of(Ctid.of(486487, 1), Ctid.of(513513, 185)));

    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidLegacyQueryPlan(new Ctid("(1314328,123)"), 9805450321L, 8192L, 45, GIGABYTE, 10005);
    expected = List.of(
        Pair.of(Ctid.of("(1314328,124)"), Ctid.of(1314827, 10005)),
        Pair.of(Ctid.of("(1314828,1)"), Ctid.of(1315326, 10005)),
        Pair.of(Ctid.of("(1315327,1)"), Ctid.of(1315825, 10005)),
        Pair.of(Ctid.of("(1315826,1)"), Ctid.of(1316324, 10005)),
        Pair.of(Ctid.of("(1316325,1)"), Ctid.of(1316823, 10005)));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidLegacyQueryPlan(Ctid.of(0, 0), 380545L, 8192L, 45, GIGABYTE, 55);
    expected = List.of(Pair.of(Ctid.of(0, 1), Ctid.of(90909, 55)));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidLegacyQueryPlan(Ctid.of(9876, 5432), 380545L, 8192L, 45, GIGABYTE, 5);
    expected = List.of(
        Pair.of(Ctid.of(9877, 1), Ctid.of(1009877, 5)));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidLegacyQueryPlan(Ctid.ZERO, 4096L, 8192L, 45, GIGABYTE, 226);
    expected = List.of(
        Pair.of(Ctid.of(0, 1), Ctid.of(22123, 226)));
    assertEquals(expected, chunks);

    // Simulate an empty table - expected to generate an empty query plan
    chunks = InitialSyncCtidIterator.ctidLegacyQueryPlan(Ctid.ZERO, 4096L, 8192L, 45, GIGABYTE, 1);
    expected = List.of(Pair.of(Ctid.of(0, 1), Ctid.of(5000000, 1)));
    assertEquals(expected, chunks);

    chunks = InitialSyncCtidIterator.ctidLegacyQueryPlan(Ctid.of(8, 1), 819200L, 81920L, 50, EIGHT_KB, 1);
    expected = List.of(Pair.of(Ctid.of(9, 1), Ctid.of(10, 1)), Pair.of(Ctid.of(11, 1), Ctid.of(11, 1)));
    assertEquals(expected, chunks);
  }

}
