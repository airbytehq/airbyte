import {
  AttemptFailureReason,
  AttemptFailureType,
  AttemptRead,
  JobStatus,
  SynchronousJobRead,
} from "core/request/AirbyteClient";

import { JobsWithJobs } from "./types";

export const getFailureFromAttempt = (attempt: AttemptRead): AttemptFailureReason | undefined =>
  attempt.failureSummary?.failures[0];

export const isCancelledAttempt = (attempt: AttemptRead): boolean =>
  attempt.failureSummary?.failures.some(({ failureType }) => failureType === AttemptFailureType.manual_cancellation) ??
  false;

export const didJobSucceed = (job: SynchronousJobRead | JobsWithJobs): boolean =>
  "succeeded" in job ? job.succeeded : getJobStatus(job) !== "failed";

export const getJobStatus: (job: SynchronousJobRead | JobsWithJobs) => JobStatus = (job) =>
  "succeeded" in job ? (job.succeeded ? JobStatus.succeeded : JobStatus.failed) : job.job.status;

export const getJobAttempts: (job: SynchronousJobRead | JobsWithJobs) => AttemptRead[] | undefined = (job) =>
  "attempts" in job ? job.attempts : undefined;

export const getJobId = (job: SynchronousJobRead | JobsWithJobs): string | number =>
  "id" in job ? job.id : job.job.id;
