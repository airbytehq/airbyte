import { datadogRum } from "@datadog/browser-rum";

import { config } from "config";

export const loadDatadog = (): void => {
  const {
    webappTag,
    datadog: { applicationId, clientToken, site, service },
  } = config;

  if (!applicationId || !clientToken) {
    return;
  }

  datadogRum.init({
    applicationId,
    clientToken,
    site,
    service,
    version: webappTag,
    sampleRate: 100,
    sessionReplaySampleRate: 0,
    trackInteractions: false,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: "mask-user-input",
  });

  datadogRum.startSessionReplayRecording();
};
