import { AttemptRead, AttemptStatus } from "core/request/AirbyteClient";

export const progressBarCalculations = (latestAttempt: AttemptRead) => {
  let numeratorRecords = 0;
  let denominatorRecords = 0;
  let totalPercentRecords = 0;
  let numeratorBytes = 0;
  let denominatorBytes = 0;
  let elapsedTimeMS = 0;
  let timeRemaining = 0;
  let displayProgressBar = true;

  if (
    latestAttempt.totalStats?.recordsEmitted !== undefined &&
    latestAttempt.totalStats?.estimatedRecords !== undefined &&
    latestAttempt.totalStats?.bytesEmitted !== undefined &&
    latestAttempt.totalStats?.estimatedBytes !== undefined
  ) {
    numeratorRecords = latestAttempt.totalStats.recordsEmitted;
    denominatorRecords = latestAttempt.totalStats.estimatedRecords;
    numeratorBytes = latestAttempt.totalStats.bytesEmitted;
    denominatorBytes = latestAttempt.totalStats.estimatedBytes;
  } else if (latestAttempt.streamStats) {
    for (const stream of latestAttempt.streamStats) {
      numeratorRecords += stream.stats.recordsEmitted ?? 0;
      denominatorRecords += stream.stats.estimatedRecords ?? 0;
      numeratorBytes += stream.stats.bytesEmitted ?? 0;
      denominatorBytes += stream.stats.estimatedBytes ?? 0;
    }
  }

  totalPercentRecords = denominatorRecords > 0 ? numeratorRecords / denominatorRecords : 0;

  // chose to estimate time remaining based on records rather than bytes
  if (latestAttempt.status === AttemptStatus.running && denominatorRecords > 0) {
    elapsedTimeMS = Date.now() - latestAttempt.createdAt * 1000;
    timeRemaining = Math.floor(elapsedTimeMS / totalPercentRecords) * (1 - totalPercentRecords); // in ms
  } else {
    displayProgressBar = false;
  }

  return {
    displayProgressBar,
    totalPercentRecords,
    timeRemaining,
    numeratorBytes,
    numeratorRecords,
    denominatorRecords,
    denominatorBytes,
    elapsedTimeMS,
  };
};
