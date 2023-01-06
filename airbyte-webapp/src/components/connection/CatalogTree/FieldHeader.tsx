import React, { memo } from "react";
import { FormattedMessage } from "react-intl";

import { useExperiment } from "hooks/services/Experiment";

import { HeaderCell, SyncHeaderContainer, NameContainer } from "./styles";

const FieldHeaderInner: React.FC = () => {
  const isColumnSelectionEnabled = useExperiment("connection.columnSelection", false);

  return (
    <>
      {isColumnSelectionEnabled && (
        <HeaderCell light flex={0}>
          <SyncHeaderContainer>
            <FormattedMessage id="form.field.sync" />
          </SyncHeaderContainer>
        </HeaderCell>
      )}
      <HeaderCell light flex={1.5}>
        {!isColumnSelectionEnabled && (
          <NameContainer>
            <FormattedMessage id="form.field.name" />
          </NameContainer>
        )}
        {isColumnSelectionEnabled && <FormattedMessage id="form.field.name" />}
      </HeaderCell>
      <HeaderCell light>
        <FormattedMessage id="form.field.dataType" />
      </HeaderCell>
      <HeaderCell light>
        <FormattedMessage id="form.field.cursorField" />
      </HeaderCell>
      <HeaderCell light>
        <FormattedMessage id="form.field.primaryKey" />
      </HeaderCell>
      <HeaderCell light flex={1.5}>
        <FormattedMessage id="form.field.destinationName" />
      </HeaderCell>
    </>
  );
};

export const FieldHeader = memo(FieldHeaderInner);
