import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard } from "components";
import useWorkspace from "components/hooks/services/useWorkspaceHook";
import useWorkspaceEditor from "pages/SettingsPage/components/useWorkspaceEditor";
import HeadTitle from "components/HeadTitle";
import AccountForm from "./components/AccountForm";

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
