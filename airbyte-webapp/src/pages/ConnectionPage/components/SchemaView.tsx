import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../components/ContentCard";
import Button from "../../../components/Button";
import TreeView from "../../../components/TreeView";
import { Connection } from "../../../core/resources/Connection";
import {
  constructInitialSchemaState,
  constructNewSchema
} from "../../../core/helpers";
import EmptyResource from "../../../components/EmptyResourceBlock";
import useConnection from "../../../components/hooks/services/useConnectionHook";

type IProps = {
  connection: Connection;
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

const SchemaView: React.FC<IProps> = ({ connection, afterSave }) => {
  const { updateConnection } = useConnection();
  const { formSyncSchema, initialChecked, allSchemaChecked } = useMemo(
    () => constructInitialSchemaState(connection.syncSchema),
    [connection.syncSchema]
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
    const newSyncSchema = constructNewSchema(
      connection.syncSchema,
      checkedState
    );

    await updateConnection({
      connectionId: connection.connectionId,
      status: connection.status,
      syncSchema: newSyncSchema,
      schedule: connection.schedule
    });
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
        {!connection.syncSchema.streams.length ? (
          <EmptyResource text={<FormattedMessage id="sources.emptySchema" />} />
        ) : (
          <TreeView
            nodes={formSyncSchema}
            checked={checkedState}
            onCheck={onCheckAction}
            checkedAll={allSchemaChecked}
          />
        )}
      </ContentCard>
    </Content>
  );
};

export default SchemaView;
