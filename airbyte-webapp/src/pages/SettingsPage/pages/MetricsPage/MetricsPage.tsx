import React from "react";
import { FormattedMessage } from "react-intl";
import useWorkspace from "components/hooks/services/useWorkspace";
import HeadTitle from "components/HeadTitle";
import MetricsForm from "./components/MetricsForm";
import useWorkspaceEditor from "../../components/useWorkspaceEditor";

import { Content, SettingsCard } from "../SettingsComponents";

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
