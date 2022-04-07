import React, { memo, useMemo } from "react";
import styled from "styled-components";
import { useIntl } from "react-intl";

import { Cell, CheckBox, RadioButton } from "components";

import DataTypeCell from "./components/DataTypeCell";
import { NameContainer } from "./styles";

interface FieldRowProps {
  name: string;
  path: string[];
  type: string;
  format?: string;
  airbyte_type?: string;
  nullable?: boolean;
  destinationName: string;
  isPrimaryKey: boolean;
  isPrimaryKeyEnabled: boolean;
  isCursor: boolean;
  isCursorEnabled: boolean;
  anyOf?: unknown[];
  oneOf?: unknown[];

  onPrimaryKeyChange: (pk: string[]) => void;
  onCursorChange: (cs: string[]) => void;
}

const FirstCell = styled(Cell)`
  margin-left: -10px;
`;

const LastCell = styled(Cell)`
  margin-right: -10px;
`;

const FieldRowInner: React.FC<FieldRowProps> = ({ onPrimaryKeyChange, onCursorChange, path, ...props }) => {
  const { formatMessage } = useIntl();
  const dataType = useMemo(() => {
    if (props.oneOf || props.anyOf) {
      return "union";
    }
    if (!props.anyOf && !props.oneOf && !props.airbyte_type && !props.format && !props.type) {
      return "unknown";
    }
    return props.airbyte_type ?? props.format ?? props.type;
  }, [props.airbyte_type, props.anyOf, props.format, props.oneOf, props.type]);
  const dataTypeFormatted = useMemo(
    () => formatMessage({ id: `airbyte.datatype.${dataType}` }),
    [dataType, formatMessage]
  );

  return (
    <>
      <FirstCell ellipsis flex={1.5}>
        <NameContainer title={props.name}>{props.name}</NameContainer>
      </FirstCell>
      <DataTypeCell nullable={props.nullable}>{dataTypeFormatted}</DataTypeCell>
      <Cell>
        {props.isCursorEnabled && <RadioButton checked={props.isCursor} onChange={() => onCursorChange(path)} />}
      </Cell>
      <Cell>
        {props.isPrimaryKeyEnabled && (
          <CheckBox checked={props.isPrimaryKey} onChange={() => onPrimaryKeyChange(path)} />
        )}
      </Cell>
      <LastCell ellipsis title={props.destinationName} flex={1.5}>
        {props.destinationName}
      </LastCell>
    </>
  );
};

export const FieldRow = memo(FieldRowInner);
