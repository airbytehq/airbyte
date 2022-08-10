import React from "react";
import { FormattedMessage } from "react-intl";

import HeadTitle from "components/HeadTitle";

import useWorkspaceEditor from "pages/SettingsPage/components/useWorkspaceEditor";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import { Content, SettingsCard } from "../SettingsComponents";
import AccountForm from "./components/AccountForm";

const AccountPage: React.FC = () => {
  const workspace = useCurrentWorkspace();
  const {
    errorMessage,
    successMessage,
    // loading,
    updateData,
  } = useWorkspaceEditor();

  const onSubmit = async (data: { email: string }) => {
    await updateData({
      ...workspace,
      ...data,
      news: !!workspace.news,
      anonymousDataCollection: !!workspace.anonymousDataCollection,
      securityUpdates: !!workspace.securityUpdates,
    });
  };

  return (
    <>
      <HeadTitle titles={[{ id: "sidebar.settings" }, { id: "settings.account" }]} />
      <SettingsCard title={<FormattedMessage id="settings.accountSettings" />}>
        <Content>
          <AccountForm
            email={workspace.email ?? ""}
            onSubmit={onSubmit}
            errorMessage={errorMessage}
            successMessage={successMessage}
          />
        </Content>
      </SettingsCard>
    </>
  );
};

export default AccountPage;
