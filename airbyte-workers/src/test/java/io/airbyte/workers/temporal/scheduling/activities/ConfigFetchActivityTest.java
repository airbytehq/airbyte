package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class ConfigFetchActivityTest {

  @Mock
  private ConfigPersistence configPersistence;

  @Mock
  private JobPersistence jobPersistence;

  private ConfigFetchActivity configFetchActivity;

  @BeforeEach
  public void setUp() {
    //configFetchActivity = new ConfigFetchActivityImpl(jobPersistence, configPersistence);
  }
}
