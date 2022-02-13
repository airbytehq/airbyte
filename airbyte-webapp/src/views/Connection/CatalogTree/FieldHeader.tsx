import React, { memo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";

const Name = styled.div`
  padding-left: 30px;
`;

const HeaderCell = styled(Cell)`
  font-size: 10px;
  line-height: 13px;
`;

const FieldHeaderInner: React.FC = () => (
  <>
    <HeaderCell lighter flex={1.5}>
      <Name>
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
