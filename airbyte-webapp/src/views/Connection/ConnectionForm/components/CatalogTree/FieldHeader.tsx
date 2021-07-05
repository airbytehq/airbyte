import React from "react";
import { Cell, Row } from "components/SimpleTableComponents";

const FieldHeader: React.FC = () => {
  return (
    <Row>
      <Cell>field.name</Cell>
      <Cell>field.dataType</Cell>
      <Cell>field.destinationName</Cell>
      <Cell>field.primaryKey</Cell>
      <Cell>field.cursorField</Cell>
    </Row>
  );
};
export { FieldHeader };
