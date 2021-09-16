import React, { memo } from "react";
import styled from "styled-components";
import { Cell } from "components/SimpleTableComponents";
import { CheckBox, RadioButton } from "components";
import DataTypeCell from "./components/DataTypeCell";

interface FieldRowProps {
  name: string;
  path: string[];
  type: string;
  nullable?: boolean;
  destinationName: string;
  isPrimaryKey: boolean;
  isPrimaryKeyEnabled: boolean;
  isCursor: boolean;
  isCursorEnabled: boolean;
  depth?: number;

  onPrimaryKeyChange: (pk: string[]) => void;
  onCursorChange: (cs: string[]) => void;
}

const FirstCell = styled(Cell)<{ depth?: number }>`
  margin-left: ${({ depth }) => (depth ? depth * -38 : 0)}px;
`;

const NameContainer = styled.span<{ depth?: number }>`
  padding-left: ${({ depth }) => (depth ? depth * 59 : 0)}px;
`;

const LastCell = styled(Cell)<{ depth?: number }>`
  margin-right: ${({ depth }) => (depth ? depth * -38 : 0)}px;
`;

const RadiobuttonContainer = styled.div<{ depth?: number }>`
  padding-right: ${({ depth }) => (depth ? depth * 38 : 0)}px;
`;

const FieldRowInner: React.FC<FieldRowProps> = ({
  onPrimaryKeyChange,
  onCursorChange,
  path,
  ...props
}) => {
  return (
    <>
      <FirstCell ellipsis depth={props.depth} flex={1.5}>
        <NameContainer depth={props.depth} title={props.name}>
          {props.name}
        </NameContainer>
      </FirstCell>
      <Cell />
      <DataTypeCell nullable={props.nullable}>{props.type}</DataTypeCell>
      <Cell ellipsis title={props.destinationName}>
        {props.destinationName}
      </Cell>
      <Cell flex={1.5} />
      <Cell>
        {props.isPrimaryKeyEnabled && (
          <CheckBox
            checked={props.isPrimaryKey}
            onChange={() => onPrimaryKeyChange(path)}
          />
        )}
      </Cell>
      <LastCell depth={props.depth}>
        {props.isCursorEnabled && (
          <RadiobuttonContainer depth={props.depth}>
            <RadioButton
              checked={props.isCursor}
              onChange={() => onCursorChange(path)}
            />
          </RadiobuttonContainer>
        )}
      </LastCell>
    </>
  );
};

const FieldRow = memo(FieldRowInner);
export { FieldRow };
