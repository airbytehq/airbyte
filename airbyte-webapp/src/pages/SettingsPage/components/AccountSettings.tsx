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
  const [feedback, setFeedback] = useState({});

  const onSubmit = async (data: {
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    const editField =
      data.securityUpdates !== workspace.securityUpdates
        ? "securityUpdates"
        : data.news !== workspace.news
        ? "news"
        : "anonymousDataCollection";

    setFeedback({ ...feedback, [editField]: "loading" });
    await updatePreferences(data);
    setFeedback({ ...feedback, [editField]: "success" });
  };

  return (
    <SettingsCard title={<FormattedMessage id="settings.accountSettings" />}>
      <Content>
        <PreferencesForm
          onSubmit={onSubmit}
          isEdit
          feedback={feedback}
          values={{
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
