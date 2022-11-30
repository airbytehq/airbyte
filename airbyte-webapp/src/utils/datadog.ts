import { datadogRum } from "@datadog/browser-rum";
export const loadDatadog = (): void => {
  const applicationId = window.REACT_APP_DATADOG_APPLICATION_ID ?? process.env.REACT_APP_DATADOG_APPLICATION_ID;
  if (!applicationId) {
    return;
  }

  const clientToken = window.REACT_APP_DATADOG_CLIENT_TOKEN ?? process.env.REACT_APP_DATADOG_CLIENT_TOKEN;
  const site = window.REACT_APP_DATADOG_SITE ?? process.env.REACT_APP_DATADOG_SITE;
  const service = window.REACT_APP_DATADOG_SERVICE ?? process.env.REACT_APP_DATADOG_SERVICE;
  const version = window.REACT_APP_WEBAPP_TAG ?? process.env.REACT_APP_WEBAPP_TAG ?? "dev";

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
