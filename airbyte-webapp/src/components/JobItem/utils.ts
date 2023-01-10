import { AttemptFailureReason, AttemptFailureType, AttemptRead } from "core/request/AirbyteClient";

export const getFailureFromAttempt = (attempt: AttemptRead): AttemptFailureReason | undefined =>
  attempt.failureSummary?.failures[0];

export const isCancelledAttempt = (attempt: AttemptRead): boolean =>
  attempt.failureSummary?.failures.some(({ failureType }) => failureType === AttemptFailureType.manual_cancellation) ??
  false;
