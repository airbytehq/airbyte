import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard } from "components";
import useWorkspace from "components/hooks/services/useWorkspaceHook";
import HeadTitle from "components/HeadTitle";
import MetricsForm from "./components/MetricsForm";
import useWorkspaceEditor from "../../components/useWorkspaceEditor";

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
  const { workspace } = useWorkspace();

  const {
    errorMessage,
    successMessage,
    loading,
    updateData,
  } = useWorkspaceEditor();

  const onChange = async (data: { anonymousDataCollection: boolean }) => {
    await updateData({ ...workspace, ...data });
  };

  return (
    <>
      <HeadTitle
        titles={[{ id: "sidebar.settings" }, { id: "settings.metrics" }]}
      />
      <SettingsCard title={<FormattedMessage id="settings.metricsSettings" />}>
        <Content>
          <MetricsForm
            onChange={onChange}
            anonymousDataCollection={workspace.anonymousDataCollection}
            successMessage={successMessage}
            errorMessage={errorMessage}
            isLoading={loading}
          />
        </Content>
      </SettingsCard>
    </>
  );
};

export default MetricsPage;
