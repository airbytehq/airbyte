package io.airbyte.cdk.db.jdbc;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import javax.xml.bind.DatatypeConverter;

class AbstractJdbcCompatibleSourceOperationsTest {

  @Test
  void testRowToJson() {
    DatatypeConverter.parseBase64Binary("n61enu/ftEkAAAAAAAAAAA==");
  }

}