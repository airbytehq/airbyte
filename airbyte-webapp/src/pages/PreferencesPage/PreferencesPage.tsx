import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { PageViewContainer } from "../../components/CenteredPageComponents";
import { H1 } from "components";
import { PreferencesForm } from "components";
import config from "../../config";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";
import useWorkspace from "../../components/hooks/services/useWorkspaceHook";
import styled from "styled-components";
import HeadTitle from "components/HeadTitle";

const Title = styled(H1)`
  margin-bottom: 47px;
`;

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
      <HeadTitle titles={[{ id: "preferences.headTitle" }]} />
      <Title center>
        <FormattedMessage id={"preferences.title"} />
      </Title>
      <PreferencesForm onSubmit={onSubmit} />
    </PageViewContainer>
  );
};

export default PreferencesPage;
