package io.airbyte.cdk.integrations.base.consumers;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.util.function.Consumer;

/**
 * Example of what this might look like in the Airbyte CDK in order to make
 * the output record collector injectable.
 */
@Singleton
@Named("outputRecordCollector")
public class DefaultOutputRecordCollector implements Consumer<AirbyteMessage> {
    @Override
    public void accept(final AirbyteMessage airbyteMessage) {
        System.out.println(Jsons.serialize(airbyteMessage));
    }
}
