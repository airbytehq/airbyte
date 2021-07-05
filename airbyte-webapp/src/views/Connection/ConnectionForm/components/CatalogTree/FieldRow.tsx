import React from "react";
import { Cell } from "components/SimpleTableComponents";
import { CheckBox, RadioButton } from "components";

interface FieldRowProps {
  name: string;
  type: string;
  nullable?: boolean;
  destinationName: string;
  isPrimaryKey: boolean;
  isPrimaryKeyEnabled: boolean;
  isCursor: boolean;
  isCursorEnabled: boolean;

  onPrimaryKeyChange: () => void;
  onCursorChange: () => void;
}

const FieldRow: React.FC<FieldRowProps> = (props) => {
  return (
    <>
      <Cell>{props.name}</Cell>
      <Cell>
        {props.type}
        {props.nullable}
      </Cell>
      <Cell>{props.destinationName}</Cell>
      <Cell>
        <CheckBox checked={props.isPrimaryKey} />
      </Cell>
      <Cell>
        <RadioButton checked={props.isCursor} />
      </Cell>
    </>
  );
};

export { FieldRow };
