import { datadogRum } from "@datadog/browser-rum";
export const loadDatadog = (): void => {
  const applicationId = window.REACT_APP_DATADOG_APPLICATION_ID ?? import.meta.env.REACT_APP_DATADOG_APPLICATION_ID;
  if (!applicationId) {
    return;
  }

  const clientToken = window.REACT_APP_DATADOG_CLIENT_TOKEN ?? import.meta.env.REACT_APP_DATADOG_CLIENT_TOKEN;
  const site = window.REACT_APP_DATADOG_SITE ?? import.meta.env.REACT_APP_DATADOG_SITE;
  const service = window.REACT_APP_DATADOG_SERVICE ?? import.meta.env.REACT_APP_DATADOG_SERVICE;
  const version = window.REACT_APP_WEBAPP_TAG ?? import.meta.env.REACT_APP_WEBAPP_TAG ?? "dev";

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
