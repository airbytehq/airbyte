import React, { useMemo } from "react";

import { HeadTitle } from "components/common/HeadTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

import { WebHookForm } from "./components/WebHookForm";

const NotificationPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SETTINGS_NOTIFICATION);

  const workspace = useCurrentWorkspace();
  const firstNotification = workspace.notifications?.[0];
  const initialValues = useMemo(
    () => ({
      webhook: firstNotification?.slackConfiguration?.webhook,
      sendOnSuccess: firstNotification?.sendOnSuccess,
      sendOnFailure: firstNotification?.sendOnFailure,
    }),
    [firstNotification]
  );

  return (
    <>
      <HeadTitle titles={[{ id: "sidebar.settings" }, { id: "settings.notifications" }]} />
      <WebHookForm webhook={initialValues} />
    </>
  );
};

export default NotificationPage;
