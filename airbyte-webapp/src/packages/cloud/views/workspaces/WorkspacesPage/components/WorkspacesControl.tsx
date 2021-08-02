import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button, ContentCard } from "components";
import CreateWorkspaceForm from "./CreateWorkspaceForm";

const CreateButton = styled(Button)`
  margin-top: 25px;
`;
const FormContent = styled(ContentCard)`
  padding: 15px 20px 16px 20px;
`;

const WorkspacesControl: React.FC = () => {
  const [isEditMode, setIsEditMode] = useState(false);

  //TODO: add action
  const onSubmit = () => {
    setIsEditMode(false);
  };

  return isEditMode ? (
    <FormContent>
      <CreateWorkspaceForm onSubmit={onSubmit} />
    </FormContent>
  ) : (
    <CreateButton onClick={() => setIsEditMode(true)}>
      <FormattedMessage id="workspaces.createNew" />
    </CreateButton>
  );
};

export default WorkspacesControl;
