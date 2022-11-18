import { AttemptRead, AttemptStatus } from "core/request/AirbyteClient";

export const progressBarCalculations = (latestAttempt: AttemptRead) => {
  let numeratorRecords = -1;
  let denominatorRecords = -1;
  let totalPercentRecords = -1;
  let numeratorBytes = -1;
  let denominatorBytes = -1;
  let elapsedTimeMS = -1;
  let timeRemaining = -1;
  let displayProgressBar = true;

  let countTotalsFromStreams = true;
  if (
    latestAttempt.totalStats?.recordsEmitted &&
    latestAttempt.totalStats?.estimatedRecords &&
    latestAttempt.totalStats?.bytesEmitted &&
    latestAttempt.totalStats?.estimatedBytes
  ) {
    countTotalsFromStreams = false;
    numeratorRecords = latestAttempt.totalStats.recordsEmitted;
    denominatorRecords = latestAttempt.totalStats.estimatedRecords;
    numeratorBytes = latestAttempt.totalStats.bytesEmitted;
    denominatorBytes = latestAttempt.totalStats.estimatedBytes;
  } else if (!latestAttempt.totalStats && latestAttempt.streamStats) {
    for (const stream of latestAttempt.streamStats) {
      if (countTotalsFromStreams) {
        numeratorRecords += stream.stats.recordsEmitted ?? 0;
        denominatorRecords += stream.stats.estimatedRecords ?? 0;
        numeratorBytes += stream.stats.bytesEmitted ?? 0;
        denominatorBytes += stream.stats.estimatedBytes ?? 0;
      }
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
