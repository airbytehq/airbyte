import React from "react";
import { FormattedMessage } from "react-intl";
import { useToggle } from "react-use";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import CreateWorkspaceForm from "./CreateWorkspaceForm";
import styles from "./WorkspaceControl.module.scss";

const FormContent = styled(Card)`
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
    <Button className={styles.createButton} onClick={toggleMode} data-testid="workspaces.createNew">
      <FormattedMessage id="workspaces.createNew" />
    </Button>
  );
};

export default WorkspacesControl;
