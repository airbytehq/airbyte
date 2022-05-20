package io.airbyte.integrations.destination.bigquery;

import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class BigQueryTestDataComparator extends AdvancedTestDataComparator {

    private final StandardNameTransformer namingResolver = new StandardNameTransformer();

    @Override
    protected List<String> resolveIdentifier(final String identifier) {
        final List<String> result = new ArrayList<>();
        result.add(identifier);
        result.add(namingResolver.getIdentifier(identifier));
        return result;
    }

    private Instant getInstantFromEpoch(String epochValue) {
        return Instant.ofEpochSecond(Long.parseLong(epochValue.replaceAll(".0$", "")));
    }

    @Override
    protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
        return ZonedDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
    }

    @Override
    protected boolean compareDateTimeValues(String airbyteMessageValue, String destinationValue) {
        var format = DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT);
        LocalDateTime dateTime = LocalDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
        return super.compareDateTimeValues(airbyteMessageValue, format.format(dateTime));
    }
}
