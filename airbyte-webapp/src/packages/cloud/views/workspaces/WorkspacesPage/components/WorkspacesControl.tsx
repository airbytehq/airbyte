import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useToggle } from "react-use";

import { Button, ContentCard } from "components";
import CreateWorkspaceForm from "./CreateWorkspaceForm";

const CreateButton = styled(Button)`
  margin-top: 25px;
`;
const FormContent = styled(ContentCard)`
  padding: 15px 20px 16px 20px;
`;

const WorkspacesControl: React.FC<{
  onSubmit: (name: string) => Promise<unknown>;
}> = (props) => {
  const [isEditMode, toggleMode] = useToggle(false);

  const onSubmit = async (values: { name: string }) => {
    await props.onSubmit(values.name);
    toggleMode();
  };

  return isEditMode ? (
    <FormContent>
      <CreateWorkspaceForm onSubmit={onSubmit} />
    </FormContent>
  ) : (
    <CreateButton onClick={toggleMode}>
      <FormattedMessage id="workspaces.createNew" />
    </CreateButton>
  );
};

export default WorkspacesControl;
