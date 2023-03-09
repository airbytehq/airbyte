import React from "react";
import { FormattedMessage } from "react-intl";

import { HeadTitle } from "components/common/HeadTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import MetricsForm from "./components/MetricsForm";
import useWorkspaceEditor from "../../components/useWorkspaceEditor";
import { Content, SettingsCard } from "../SettingsComponents";

const MetricsPage: React.FC = () => {
  const workspace = useCurrentWorkspace();
  const { errorMessage, successMessage, loading, updateData } = useWorkspaceEditor();

  useTrackPage(PageTrackingCodes.SETTINGS_METRICS);
  const onChange = async (data: { anonymousDataCollection: boolean }) => {
    await updateData({ ...workspace, ...data, news: !!workspace.news, securityUpdates: !!workspace.securityUpdates });
  };

  return (
    <>
      <HeadTitle titles={[{ id: "sidebar.settings" }, { id: "settings.metrics" }]} />
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
