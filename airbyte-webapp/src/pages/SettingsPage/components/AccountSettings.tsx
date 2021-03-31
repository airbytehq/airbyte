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
  const [errorMessage, setErrorMessage] = useState<React.ReactNode>(null);
  const [successMessage, setSuccessMessage] = useState<React.ReactNode>(null);

  const onSubmit = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await updatePreferences(data);
      setSuccessMessage(<FormattedMessage id="form.changesSaved" />);
    } catch (e) {
      setErrorMessage(<FormattedMessage id="form.someError" />);
    }
  };

  return (
    <SettingsCard title={<FormattedMessage id="settings.accountSettings" />}>
      <Content>
        <PreferencesForm
          errorMessage={errorMessage}
          successMessage={successMessage}
          onSubmit={onSubmit}
          isEdit
          preferencesValues={{
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
