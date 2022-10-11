export const loadDatadog = async (): Promise<void> => {
  const applicationId = process.env.REACT_APP_DATADOG_APPLICATION_ID ?? window.REACT_APP_DATADOG_APPLICATION_ID;
  if (!applicationId) {
    return;
  }

  const { datadogRum } = await import("@datadog/browser-rum");

  const clientToken = process.env.REACT_APP_DATADOG_CLIENT_TOKEN ?? window.REACT_APP_DATADOG_CLIENT_TOKEN;
  const site = process.env.REACT_APP_DATADOG_SITE ?? window.REACT_APP_DATADOG_SITE;
  const service = process.env.REACT_APP_DATADOG_SERVICE ?? window.REACT_APP_DATADOG_SERVICE;
  const version = process.env.REACT_APP_WEBAPP_TAG ?? window.REACT_APP_WEBAPP_TAG ?? "dev";

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
