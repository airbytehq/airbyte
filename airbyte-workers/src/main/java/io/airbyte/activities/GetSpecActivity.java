package io.airbyte.activities;

import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.OutputAndStatus;
import io.temporal.activity.ActivityInterface;

import java.nio.file.Path;

@ActivityInterface
public interface GetSpecActivity {

    ConnectorSpecification run(String dockerImage) throws Exception;

}
