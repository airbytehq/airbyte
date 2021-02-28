import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { PageViewContainer } from "../../components/CenteredPageComponents";
import { H1 } from "components/Titles";
import PreferencesForm from "./components/PreferencesForm";
import config from "../../config";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";
import useWorkspace from "../../components/hooks/services/useWorkspaceHook";

const PreferencesPage: React.FC = () => {
  useEffect(() => {
    AnalyticsService.page("Preferences Page");
  }, []);

  const { setInitialSetupConfig } = useWorkspace();

  const onSubmit = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await setInitialSetupConfig(data);

    AnalyticsService.track("Specified Preferences", {
      user_id: config.ui.workspaceId,
      email: data.email,
      anonymized: data.anonymousDataCollection,
      subscribed_newsletter: data.news,
      subscribed_security: data.securityUpdates,
    });
  };

  return (
    <PageViewContainer>
      <H1 center>
        <FormattedMessage id={"preferences.title"} />
      </H1>
      <PreferencesForm onSubmit={onSubmit} />
    </PageViewContainer>
  );
};

export default PreferencesPage;
