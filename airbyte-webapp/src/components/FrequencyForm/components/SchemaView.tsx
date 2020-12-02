import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import TreeView, { INode } from "../../TreeView/TreeView";
import { Cell, Header, LightCell } from "../../SimpleTableComponents";

type IProps = {
  schema: INode[];
  allSchemaChecked: string[];
  checkedState: string[];
  onCheckAction: (data: string[]) => void;
};

const TreeViewContainer = styled.div`
  width: 100%;
  background: ${({ theme }) => theme.greyColor0};
  margin-bottom: 29px;
  border-radius: 4px;
  overflow: hidden;
`;

const SchemaView: React.FC<IProps> = ({
  schema,
  checkedState,
  allSchemaChecked,
  onCheckAction
}) => {
  return (
    <>
      <Header>
        <Cell flex={2}>
          <FormattedMessage id="form.dataSync" />
        </Cell>
        <LightCell>
          <FormattedMessage id="form.dataType" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.cleanedName" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.syncSettings" />
        </LightCell>
      </Header>
      <TreeViewContainer>
        <TreeView
          checkedAll={allSchemaChecked}
          nodes={schema}
          onCheck={onCheckAction}
          checked={checkedState}
        />
      </TreeViewContainer>
    </>
  );
};

export default SchemaView;
