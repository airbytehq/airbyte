import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import { PageViewContainer } from "../../components/CenteredPageComponents";
import { H1 } from "../../components/Titles";
import PreferencesForm from "./components/PreferencesForm";
import WorkspaceResource from "../../core/resources/Workspace";
import config from "../../config";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";

const PreferencesPage: React.FC = () => {
  useEffect(() => {
    AnalyticsService.page("Preferences Page");
  }, []);

  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());

  const onSubmit = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await updateWorkspace(
      {},
      {
        workspaceId: config.ui.workspaceId,
        initialSetupComplete: true,
        onboardingComplete: false,
        ...data
      }
    );

    AnalyticsService.track("Specified Preferences", {
      user_id: config.ui.workspaceId,
      email: data.email,
      anonymized: data.anonymousDataCollection,
      subscribed_newsletter: data.news,
      subscribed_security: data.securityUpdates
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
