import React, { memo } from "react";
import { Cell } from "components/SimpleTableComponents";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

const Name = styled.div<{ depth?: number }>`
  padding-left: ${({ depth }) => (depth ? depth * 59 : 0)}px;
`;

const FieldHeaderInner: React.FC<{ depth?: number }> = (props) => (
  <>
    <Cell lighter flex={1.5}>
      <Name depth={props.depth}>
        <FormattedMessage id="form.field.name" />
      </Name>
    </Cell>
    <Cell lighter />
    <Cell lighter>
      <FormattedMessage id="form.field.dataType" />
    </Cell>
    <Cell lighter>
      <FormattedMessage id="form.field.destinationName" />
    </Cell>
    <Cell lighter flex={1.5} />
    <Cell lighter>
      <FormattedMessage id="form.field.primaryKey" />
    </Cell>
    <Cell lighter>
      <FormattedMessage id="form.field.cursorField" />
    </Cell>
  </>
);

const FieldHeader = memo(FieldHeaderInner);

export { FieldHeader };
