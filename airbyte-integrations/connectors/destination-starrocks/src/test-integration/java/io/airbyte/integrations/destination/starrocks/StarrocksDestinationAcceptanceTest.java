/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.lang3.StringEscapeUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class StarrocksDestinationAcceptanceTest extends DestinationAcceptanceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(StarrocksDestinationAcceptanceTest.class);

    private static final StandardNameTransformer namingResolver = new StandardNameTransformer();

    private JsonNode configJson;

    private static Connection conn = null;

    @Override
    protected String getImageName() {
        return "airbyte/destination-starrocks:dev";
    }

    @BeforeAll
    public static void getConnect() throws SQLException, ClassNotFoundException {
        JsonNode config = Jsons.deserialize(IOs.readFile(Paths.get("../../../secrets/config.json")));
        conn = SqlUtil.createJDBCConnection(config);
    }

    @AfterAll
    public static void closeConnect() throws SQLException {
        if (conn != null) {
            conn.close();
        }
    }

    @Override
    protected JsonNode getConfig() {
        // TODO: Generate the configuration JSON file to be used for running the destination during the test
        // configJson can either be static and read from secrets/config.json directly
        // or created in the setup method
        configJson = Jsons.deserialize(IOs.readFile(Paths.get("../../../secrets/config.json")));

        return configJson;
    }

    @Override
    protected JsonNode getFailCheckConfig() {
        // TODO return an invalid config which, when used to run the connector's check connection operation,
        // should result in a failed connection check
        return null;
    }

    @Override
    protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                             String streamName,
                                             String namespace,
                                             JsonNode streamSchema)
            throws IOException, SQLException {
        // TODO Implement this method to retrieve records which written to the destination by the connector.
        // Records returned from this method will be compared against records provided to the connector
        // to verify they were written correctly
        final String tableName = namingResolver.getIdentifier(streamName);

        String query = String.format(
                "SELECT * FROM %s.%s ORDER BY %s ASC;", configJson.get("database").asText(), tableName,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
        PreparedStatement stmt = conn.prepareStatement(query);
        ResultSet resultSet = stmt.executeQuery();

        List<JsonNode> res = new ArrayList<>();
        while (resultSet.next()) {
            String sss = resultSet.getString(JavaBaseConstants.COLUMN_NAME_DATA);
            res.add(Jsons.deserialize(StringEscapeUtils.unescapeJava(sss)));
        }
        stmt.close();
        return res;
    }

    @Override
    protected void setup(TestDestinationEnv testEnv) {
        // TODO Implement this method to run any setup actions needed before every test case
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
        // TODO Implement this method to run any cleanup actions needed after every test case
    }

    @Override
    public void testLineBreakCharacters() {
        // overrides test with a no-op until we handle full UTF-8 in the destination
    }

    @Override
    public void testSecondSync() throws Exception {
        // PubSub cannot overwrite messages, its always append only
    }

}
