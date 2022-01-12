import React, { memo } from "react";
import { Cell } from "components/SimpleTableComponents";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

const Name = styled.div<{ depth?: number }>`
  padding-left: ${({ depth }) => (depth ? depth * 30 : 0)}px;
`;

const HeaderCell = styled(Cell)`
  font-size: 10px;
  line-height: 13px;
`;

const FieldHeaderInner: React.FC<{ depth?: number }> = (props) => (
  <>
    <HeaderCell lighter flex={1.5}>
      <Name depth={props.depth}>
        <FormattedMessage id="form.field.name" />
      </Name>
    </HeaderCell>
    <HeaderCell lighter>
      <FormattedMessage id="form.field.dataType" />
    </HeaderCell>
    <HeaderCell lighter>
      <FormattedMessage id="form.field.cursorField" />
    </HeaderCell>
    <HeaderCell lighter>
      <FormattedMessage id="form.field.primaryKey" />
    </HeaderCell>
    <HeaderCell lighter flex={1.5}>
      <FormattedMessage id="form.field.destinationName" />
    </HeaderCell>
  </>
);

const FieldHeader = memo(FieldHeaderInner);

export { FieldHeader };
