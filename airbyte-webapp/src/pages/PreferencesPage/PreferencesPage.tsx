import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { PageViewContainer } from "components/CenteredPageComponents";
import HeadTitle from "components/HeadTitle";
import { H1 } from "components";
import { PreferencesForm } from "views/Settings/PreferencesForm";

import { useTrackPage } from "hooks/services/Analytics/useAnalyticsService";
import useWorkspace from "hooks/services/useWorkspace";

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
        <FormattedMessage id={"preferences.title"} />
      </Title>
      <PreferencesForm onSubmit={setInitialSetupConfig} />
    </PageViewContainer>
  );
};

export default PreferencesPage;
