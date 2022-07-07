import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { H1 } from "components";
import { PageViewContainer } from "components/CenteredPageComponents";
import HeadTitle from "components/HeadTitle";

import { useTrackPage } from "hooks/services/Analytics/useAnalyticsService";
import useWorkspace from "hooks/services/useWorkspace";
import { PreferencesForm } from "views/Settings/PreferencesForm";

const Title = styled(H1)`
  margin-bottom: 47px;
`;

const PreferencesPage: React.FC = () => {
  useTrackPage("Preferences Page");

  const { setInitialSetupConfig } = useWorkspace();

  return (
    <PageViewContainer>
      <HeadTitle titles={[{ id: "preferences.headTitle" }]} />
      <Title center>
        <FormattedMessage id="preferences.title" />
      </Title>
      <PreferencesForm onSubmit={setInitialSetupConfig} />
    </PageViewContainer>
  );
};

export default PreferencesPage;
