import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import TreeView from "../../TreeView";
import { Cell, Header, LightCell } from "../../SimpleTableComponents";
import { SyncSchema } from "../../../core/resources/Schema";

type IProps = {
  schema: SyncSchema;
  onChangeSchema: (schema: SyncSchema) => void;
};

const TreeViewContainer = styled.div`
  width: 100%;
  background: ${({ theme }) => theme.greyColor0};
  margin-bottom: 29px;
  border-radius: 4px;
`;

const SchemaView: React.FC<IProps> = ({ schema, onChangeSchema }) => {
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
        <TreeView schema={schema} onChangeSchema={onChangeSchema} />
      </TreeViewContainer>
    </>
  );
};

export default SchemaView;
