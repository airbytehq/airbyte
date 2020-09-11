import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useFetcher } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";
import TreeView from "../../../../../components/TreeView";
import ConnectionResource, {
  SyncSchema
} from "../../../../../core/resources/Connection";
import EmptySyncHistory from "./EmptySyncHistory";

type IProps = {
  connectionId: string;
  connectionStatus: string;
  syncSchema: SyncSchema;
};

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

const SchemaView: React.FC<IProps> = ({
  syncSchema,
  connectionId,
  connectionStatus
}) => {
  const updateConnection = useFetcher(ConnectionResource.updateShape());
  const initialChecked: Array<string> = [];
  syncSchema.tables.map(item =>
    item.columns.forEach(column =>
      column.selected ? initialChecked.push(column.name) : null
    )
  );

  const [disabledButtons, setDisabledButtons] = useState(true);
  const [checkedState, setCheckedState] = useState(initialChecked);

  const formSyncSchema = useMemo(
    () =>
      syncSchema.tables.map((item: any) => ({
        value: item.name,
        label: item.name,
        children: item.columns.map((column: any) => ({
          value: column.name,
          label: column.name
        }))
      })),
    [syncSchema.tables]
  );

  const onCheckAction = (data: Array<string>) => {
    setDisabledButtons(JSON.stringify(data) === JSON.stringify(initialChecked));
    setCheckedState(data);
  };

  const onCancel = () => {
    setDisabledButtons(true);
    setCheckedState(initialChecked);
  };
  const onSubmit = async () => {
    setDisabledButtons(true);
    const newSyncSchema = {
      tables: syncSchema.tables.map(item => ({
        ...item,
        columns: item.columns.map(column => ({
          ...column,
          selected: checkedState.includes(column.name)
        }))
      }))
    };

    await updateConnection(
      {},
      {
        connectionId,
        status: connectionStatus,
        syncSchema: newSyncSchema
      }
    );
  };

  return (
    <Content>
      <ButtonsContainer>
        <Button secondary disabled={disabledButtons} onClick={onCancel}>
          <FormattedMessage id="form.discardChanges" />
        </Button>
        <SaveButton disabled={disabledButtons} onClick={onSubmit}>
          <FormattedMessage id="form.saveChanges" />
        </SaveButton>
      </ButtonsContainer>
      <ContentCard>
        {!syncSchema.tables.length ? (
          <EmptySyncHistory
            text={<FormattedMessage id="sources.emptySchema" />}
          />
        ) : (
          <TreeView
            nodes={formSyncSchema}
            checked={checkedState}
            onCheck={onCheckAction}
          />
        )}
      </ContentCard>
    </Content>
  );
};

export default SchemaView;
