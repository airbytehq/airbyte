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
import {
  constructInitialSchemaState,
  constructNewSchema
} from "../../../../../core/helpers";
import EmptyResource from "../../../components/EmptyResource";

type IProps = {
  connectionId: string;
  connectionStatus: string;
  syncSchema: SyncSchema;
  afterSave: () => void;
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
  connectionStatus,
  afterSave
}) => {
  const updateConnection = useFetcher(ConnectionResource.updateShape());
  const { formSyncSchema, initialChecked } = useMemo(
    () => constructInitialSchemaState(syncSchema),
    [syncSchema]
  );

  const [disabledButtons, setDisabledButtons] = useState(true);
  const [checkedState, setCheckedState] = useState(initialChecked);

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
    const newSyncSchema = constructNewSchema(syncSchema, checkedState);

    await updateConnection(
      {},
      {
        connectionId,
        status: connectionStatus,
        syncSchema: newSyncSchema
      }
    );
    afterSave();
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
        {!syncSchema.streams.length ? (
          <EmptyResource text={<FormattedMessage id="sources.emptySchema" />} />
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
