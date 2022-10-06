import { datadogRum } from "@datadog/browser-rum";
import { useEffect, useMemo } from "react";
import { createGlobalState } from "react-use";

import { useConfig } from "config";

import { useConfig as useCloudConfig } from "../../config";

const useDatadogInited = createGlobalState(false);

export const useDatadog = (): void => {
  const { version } = useConfig();
  const { datadog: datadogConfig } = useCloudConfig();

  const [inited, setInited] = useDatadogInited();
  const enabled = useMemo(
    () => !Object.values(datadogConfig).some((value) => !value || value.trim().length === 0),
    [datadogConfig]
  );

  useEffect(() => {
    if (inited || !enabled) {
      return;
    }

    datadogRum.init({
      applicationId: datadogConfig.applicationId,
      clientToken: datadogConfig.clientToken,
      site: datadogConfig.site,
      service: datadogConfig.service,
      version,
      sampleRate: 100,
      sessionReplaySampleRate: 20,
      trackInteractions: true,
      trackResources: true,
      trackLongTasks: true,
      defaultPrivacyLevel: "mask-user-input",
    });

    datadogRum.startSessionReplayRecording();
    setInited(true);
  }, [datadogConfig, enabled, inited, setInited, version]);
};
