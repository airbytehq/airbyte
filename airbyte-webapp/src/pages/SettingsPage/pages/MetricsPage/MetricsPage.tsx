import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard } from "components";
import useWorkspace from "components/hooks/services/useWorkspaceHook";
import HeadTitle from "components/HeadTitle";
import MetricsForm from "./components/MetricsForm";

const SettingsCard = styled(ContentCard)`
  max-width: 638px;
  width: 100%;
  margin-top: 12px;

  &:first-child {
    margin-top: 0;
  }
`;

const Content = styled.div`
  padding: 27px 26px 15px;
`;

const MetricsPage: React.FC = () => {
  const { workspace, updatePreferences } = useWorkspace();
  const [errorMessage, setErrorMessage] = useState<React.ReactNode>(null);
  const [successMessage, setSuccessMessage] = useState<React.ReactNode>(null);

  const onSubmit = async (data: { anonymousDataCollection: boolean }) => {
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await updatePreferences({
        anonymousDataCollection: data.anonymousDataCollection,
        news: workspace.news,
        securityUpdates: workspace.securityUpdates,
      });
      setSuccessMessage(<FormattedMessage id="form.changesSaved" />);
    } catch (e) {
      setErrorMessage(<FormattedMessage id="form.someError" />);
    }
  };

  return (
    <>
      <HeadTitle
        titles={[{ id: "sidebar.settings" }, { id: "settings.metrics" }]}
      />
      <SettingsCard title={<FormattedMessage id="settings.metricsSettings" />}>
        <Content>
          <MetricsForm
            onSubmit={onSubmit}
            anonymousDataCollection={workspace.anonymousDataCollection}
            successMessage={successMessage}
            errorMessage={errorMessage}
          />
        </Content>
      </SettingsCard>
    </>
  );
};

export default MetricsPage;
