package io.airbyte.integrations.source.kafka.generator;

import io.airbyte.integrations.source.kafka.converter.Converter;
import io.airbyte.integrations.source.kafka.mediator.KafkaMediator;
import org.apache.avro.generic.GenericRecord;

public class AvroGenerator extends AbstractGenerator<GenericRecord> {

  public AvroGenerator(KafkaMediator<GenericRecord> mediator, Converter<GenericRecord> converter) {
    super(mediator, converter);
  }
}
