import React from "react";
import { FormattedMessage } from "react-intl";

import { HeaderCell, NameContainer } from "../styles";

export const StreamFieldsTableHeader: React.FC = React.memo(() => (
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
    <HeaderCell />
    <HeaderCell lighter flex={1.5}>
      <FormattedMessage id="form.field.name" />
    </HeaderCell>
    {/*
    In the design, but we may be unable to get the destination data type
    <HeaderCell lighter>
      <FormattedMessage id="form.field.dataType" />
    </HeaderCell>
    */}
  </>
));
