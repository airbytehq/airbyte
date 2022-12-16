/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.JobsApi;
import io.airbyte.api.model.generated.AttemptNormalizationStatusReadList;
import io.airbyte.api.model.generated.JobDebugInfoRead;
import io.airbyte.api.model.generated.JobIdRequestBody;
import io.airbyte.api.model.generated.JobInfoLightRead;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.JobListRequestBody;
import io.airbyte.api.model.generated.JobReadList;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/jobs")
@AllArgsConstructor
public class JobsApiController implements JobsApi {

  private final JobHistoryHandler jobHistoryHandler;
  private final SchedulerHandler schedulerHandler;

  @Override
  public JobInfoRead cancelJob(final JobIdRequestBody jobIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.cancelJob(jobIdRequestBody));
  }

  @Override
  public AttemptNormalizationStatusReadList getAttemptNormalizationStatusesForJob(final JobIdRequestBody jobIdRequestBody) {
    return ApiHelper.execute(() -> jobHistoryHandler.getAttemptNormalizationStatuses(jobIdRequestBody));
  }

  @Override
  public JobDebugInfoRead getJobDebugInfo(final JobIdRequestBody jobIdRequestBody) {
    return ApiHelper.execute(() -> jobHistoryHandler.getJobDebugInfo(jobIdRequestBody));
  }

  @Override
  public JobInfoRead getJobInfo(final JobIdRequestBody jobIdRequestBody) {
    return ApiHelper.execute(() -> jobHistoryHandler.getJobInfo(jobIdRequestBody));
  }

  @Override
  public JobInfoLightRead getJobInfoLight(final JobIdRequestBody jobIdRequestBody) {
    return ApiHelper.execute(() -> jobHistoryHandler.getJobInfoLight(jobIdRequestBody));
  }

  @Override
  public JobReadList listJobsFor(final JobListRequestBody jobListRequestBody) {
    return ApiHelper.execute(() -> jobHistoryHandler.listJobsFor(jobListRequestBody));
  }

}
