import { datadogRum } from "@datadog/browser-rum";

export const initDatadogRum = () => {
  const applicationId = process.env.REACT_APP_DATADOG_APPLICATION_ID ?? window.REACT_APP_DATADOG_APPLICATION_ID;
  if (!applicationId) {
    return;
  }

  const clientToken = process.env.REACT_APP_DATADOG_CLIENT_TOKEN ?? window.REACT_APP_DATADOG_CLIENT_TOKEN;
  const site = process.env.REACT_APP_DATADOG_SITE ?? window.REACT_APP_DATADOG_SITE;
  const service = process.env.REACT_APP_DATADOG_SERVICE ?? window.REACT_APP_DATADOG_SERVICE;
  const version = window.AIRBYTE_VERSION;

  datadogRum.init({
    applicationId,
    clientToken,
    site,
    service,
    version,
    sampleRate: 100,
    sessionReplaySampleRate: 0,
    trackInteractions: false,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: "mask-user-input",
  });

  datadogRum.startSessionReplayRecording();
};
