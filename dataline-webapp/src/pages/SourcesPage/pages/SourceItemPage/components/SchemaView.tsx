import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";
import TreeView from "../../../../../components/TreeView";

const Content = styled.div`
  max-width: 806px;
  margin: 18px auto;
`;

const ButtonsContainer = styled.div`
  text-align: right;
  margin-bottom: 16px;
`;

const SaveButton = styled(Button)`
  margin-left: 11px;
`;

const SchemaView: React.FC = () => {
  const initialChecked: Array<string> = [];

  const [disabledButtons, setDisabledButtons] = useState(true);
  const [checkedState, setChekedState] = useState(initialChecked);

  const nodes = [
    {
      value: "table",
      label: "Table 1",
      children: [
        { value: "c1", label: "Column 1" },
        { value: "c2", label: "Column 2" },
        { value: "c3", label: "Column 3" },
        { value: "c4", label: "Column 4" }
      ]
    },
    {
      value: "table 2",
      label: "Table 2",
      children: [
        { value: "c5", label: "Column 5" },
        { value: "c6", label: "Column 6" }
      ]
    }
  ];

  const onCheckAction = (data: Array<string>) => {
    setDisabledButtons(JSON.stringify(data) === JSON.stringify(initialChecked));
    setChekedState(data);
  };

  const onCancel = () => setChekedState(initialChecked);

  return (
    <Content>
      <ButtonsContainer>
        <Button secondary disabled={disabledButtons} onClick={onCancel}>
          <FormattedMessage id={"form.discardChanges"} />
        </Button>
        <SaveButton disabled={disabledButtons}>
          <FormattedMessage id={"form.saveChanges"} />
        </SaveButton>
      </ButtonsContainer>
      <ContentCard>
        <TreeView
          nodes={nodes}
          checked={checkedState}
          onCheck={onCheckAction}
        />
      </ContentCard>
    </Content>
  );
};

export default SchemaView;
