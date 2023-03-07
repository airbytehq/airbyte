import React, { memo } from "react";
import { FormattedMessage } from "react-intl";

import { HeaderCell, NameContainer } from "./styles";

const FieldHeaderInner: React.FC = () => (
  <>
    <HeaderCell lighter flex={1.5}>
      <NameContainer>
        <FormattedMessage id="form.field.name" />
      </NameContainer>
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
