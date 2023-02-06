import { useEffect } from "react";

import { useNotificationService } from "./Notification";

interface BuildInfo {
  build: string;
}

const INTERVAL = 10 * 1000;

export const useBuildUpdateCheck = () => {
  const { registerNotification } = useNotificationService();
  useEffect(() => {
    const intervalId = setInterval(async () => {
      try {
        const buildInfoResp = await fetch("/buildInfo.json", { cache: "no-store" });
        const buildInfo: BuildInfo = await buildInfoResp.json();

        if (buildInfo.build !== process.env.BUILD_HASH) {
          registerNotification({
            id: "webapp-updated",
            text: "Airbyte has been updated. Please reload the page.",
            nonClosable: true,
            actionBtnText: "Reload now",
            onAction: () => window.location.reload(),
          });
        }
      } catch (e) {
        // We ignore all errors from the build update check, since it's an optional check to
        // inform the user. We don't want to treat failed requests here as errors.
      }
    }, INTERVAL);

    return () => {
      clearInterval(intervalId);
    };
  }, [registerNotification]);
};
