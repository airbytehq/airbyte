import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";

import { Cell } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { RadioButton } from "components/ui/RadioButton";

import { SyncSchemaField } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { equal } from "utils/objects";
import { useTranslateDataType } from "utils/useTranslateDataType";

import DataTypeCell from "../DataTypeCell";
import { pathDisplayName } from "../PathPopout";
import { NameContainer } from "../styles";

interface StreamFieldsTableRowProps {
  isPrimaryKeyEnabled: boolean;
  isCursorEnabled: boolean;

  onPrimaryKeyChange: (pk: string[]) => void;
  onCursorChange: (cs: string[]) => void;
  field: SyncSchemaField;
  config: AirbyteStreamConfiguration | undefined;
}

const StreamFieldsTableRowComponent: React.FC<StreamFieldsTableRowProps> = ({
  onPrimaryKeyChange,
  onCursorChange,
  field,
  config,
  isCursorEnabled,
  isPrimaryKeyEnabled,
}) => {
  const dataType = useTranslateDataType(field);
  const name = pathDisplayName(field.path);

  const isCursor = equal(config?.cursorField, field.path);
  const isPrimaryKey = !!config?.primaryKey?.some((p) => equal(p, field.path));

  return (
    <>
      <Cell ellipsis flex={1.5}>
        <NameContainer title={name}>{name}</NameContainer>
      </Cell>
      <DataTypeCell>{dataType}</DataTypeCell>
      <Cell>{isCursorEnabled && <RadioButton checked={isCursor} onChange={() => onCursorChange(field.path)} />}</Cell>
      <Cell>
        {isPrimaryKeyEnabled && <CheckBox checked={isPrimaryKey} onChange={() => onPrimaryKeyChange(field.path)} />}
      </Cell>
      <Cell>
        <FontAwesomeIcon icon={faArrowRight} />
      </Cell>
      <Cell ellipsis title={field.cleanedName} flex={1.5}>
        {field.cleanedName}
      </Cell>
      {/*
      In the design, but we may be unable to get the destination data type
      <DataTypeCell>{dataType}</DataTypeCell>
      */}
    </>
  );
};

export const StreamFieldsTableRow = React.memo(StreamFieldsTableRowComponent);
