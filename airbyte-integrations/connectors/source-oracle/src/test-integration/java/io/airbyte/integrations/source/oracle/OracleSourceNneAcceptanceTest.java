package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;

public class OracleSourceNneAcceptanceTest extends OracleSourceAcceptanceTest{
    @Test
    public void testhhgjkgk() throws SQLException {
        final JsonNode clone = Jsons.clone(getConfig());
        ((ObjectNode) clone).put("encryption", Jsons.jsonNode(ImmutableMap.builder()
                .put("encryption_method", "client_nne")
                .put("encryption_algorithm", "3DES168")
                .build()));

        String algorithm = clone.get("encryption")
                .get("encryption_algorithm").asText();

        JdbcDatabase database = Databases.createJdbcDatabase(clone.get("username").asText(),
                clone.get("password").asText(),
                String.format("jdbc:oracle:thin:@//%s:%s/%s",
                        clone.get("host").asText(),
                        clone.get("port").asText(),
                        clone.get("sid").asText()),
                "oracle.jdbc.driver.OracleDriver",
                "oracle.net.encryption_client=REQUIRED;" +
                        "oracle.net.encryption_types_client=( "
                        + algorithm+" )");

        String network_service_banner = "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
        List<JsonNode> collect = database.query(network_service_banner).collect(Collectors.toList());

        assertTrue(collect.get(2).get("NETWORK_SERVICE_BANNER").asText()
                .contains("Oracle Advanced Security: "+algorithm+" encryption"));
    }

//    @Override
//    protected JsonNode getConfig() {
//        return config;
//    }
}
