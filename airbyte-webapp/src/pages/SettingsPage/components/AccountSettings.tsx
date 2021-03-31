import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard, PreferencesForm } from "components";
import useWorkspace from "components/hooks/services/useWorkspaceHook";

const SettingsCard = styled(ContentCard)`
  max-width: 638px;
  width: 100%;
`;

const Content = styled.div`
  padding: 27px 26px 15px;
`;

const AccountSettings: React.FC = () => {
  const { workspace, updatePreferences } = useWorkspace();
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const onSubmit = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    setErrorMessage("");
    setSuccessMessage("");
    await updatePreferences(data);
    setSuccessMessage("YES");
  };

  return (
    <SettingsCard title={<FormattedMessage id="settings.accountSettings" />}>
      <Content>
        <PreferencesForm
          errorMessage={errorMessage}
          successMessage={successMessage}
          onSubmit={onSubmit}
          isEdit
          values={{
            email: workspace.email,
            anonymousDataCollection: workspace.anonymousDataCollection,
            news: workspace.news,
            securityUpdates: workspace.securityUpdates,
          }}
        />
      </Content>
    </SettingsCard>
  );
};

export default AccountSettings;
