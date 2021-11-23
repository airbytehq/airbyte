import React from "react";
import { FormattedMessage } from "react-intl";
import useWorkspace from "hooks/services/useWorkspace";
import useWorkspaceEditor from "pages/SettingsPage/components/useWorkspaceEditor";
import HeadTitle from "components/HeadTitle";
import AccountForm from "./components/AccountForm";
import { Content, SettingsCard } from "../SettingsComponents";

const AccountPage: React.FC = () => {
  const { workspace } = useWorkspace();

  const {
    errorMessage,
    successMessage,
    // loading,
    updateData,
  } = useWorkspaceEditor();

  const onSubmit = async (data: { email: string }) => {
    await updateData({ ...workspace, ...data });
  };

  return (
    <>
      <HeadTitle
        titles={[{ id: "sidebar.settings" }, { id: "settings.account" }]}
      />
      <SettingsCard title={<FormattedMessage id="settings.accountSettings" />}>
        <Content>
          <AccountForm
            email={workspace.email}
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
