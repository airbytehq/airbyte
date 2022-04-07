package io.airbyte.integrations.standardtest.destination.comparator;

import com.fasterxml.jackson.databind.JsonNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class BasicTestDataComparator implements TestDataComparator {

    private static final Logger LOGGER = LoggerFactory.getLogger(BasicTestDataComparator.class);

    @Override
    public void assertSameData(List<JsonNode> expected, List<JsonNode> actual) {
        LOGGER.info("Expected data {}", expected);
        LOGGER.info("Actual data   {}", actual);
        assertEquals(expected.size(), actual.size());
        final Iterator<JsonNode> expectedIterator = expected.iterator();
        final Iterator<JsonNode> actualIterator = actual.iterator();
        while (expectedIterator.hasNext() && actualIterator.hasNext()) {
            final JsonNode expectedData = expectedIterator.next();
            final JsonNode actualData = actualIterator.next();
            final Iterator<Map.Entry<String, JsonNode>> expectedDataIterator = expectedData.fields();
            LOGGER.info("Expected row {}", expectedData);
            LOGGER.info("Actual row   {}", actualData);
            assertEquals(expectedData.size(), actualData.size(), "Unequal row size");
            while (expectedDataIterator.hasNext()) {
                final Map.Entry<String, JsonNode> expectedEntry = expectedDataIterator.next();
                final JsonNode expectedValue = expectedEntry.getValue();
                JsonNode actualValue = null;
                String key = expectedEntry.getKey();
                for (final String tmpKey : resolveIdentifier(expectedEntry.getKey())) {
                    actualValue = actualData.get(tmpKey);
                    if (actualValue != null) {
                        key = tmpKey;
                        break;
                    }
                }
                LOGGER.info("For {} Expected {} vs Actual {}", key, expectedValue, actualValue);
                assertTrue(actualData.has(key));
                assertSameValue(expectedValue, actualValue);
            }
        }
    }

    // Allows subclasses to implement custom comparison asserts
    protected void assertSameValue(final JsonNode expectedValue, final JsonNode actualValue) {
        assertEquals(expectedValue, actualValue);
    }

    protected List<String> resolveIdentifier(final String identifier) {
        final List<String> result = new ArrayList<>();
        result.add(identifier);
        return result;
    }
}
