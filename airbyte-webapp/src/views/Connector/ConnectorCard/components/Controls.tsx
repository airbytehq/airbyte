import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { FlexContainer, FlexItem } from "components/ui/Flex";

import { SynchronousJobRead } from "core/request/AirbyteClient";

import { TestCard } from "./TestCard";

interface IProps {
  formType: "source" | "destination";
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
  onCancelClick: () => void;
  onDeleteClick?: () => void;
  onRetestClick: () => void;
  onCancelTesting: () => void;
  isTestConnectionInProgress?: boolean;
  errorMessage?: React.ReactNode;
  job?: SynchronousJobRead;
  connectionTestSuccess: boolean;
  hasDefinition: boolean;
  isEditMode: boolean;
}

export const Controls: React.FC<IProps> = ({
  isTestConnectionInProgress,
  isSubmitting,
  formType,
  hasDefinition,
  isEditMode,
  dirty,
  onDeleteClick,
  onCancelClick,
  ...restProps
}) => {
  const showTestCard =
    hasDefinition &&
    (isEditMode || isTestConnectionInProgress || restProps.connectionTestSuccess || restProps.errorMessage);
  return (
    <>
      {showTestCard && (
        <TestCard
          {...restProps}
          dirty={dirty}
          formType={formType}
          isTestConnectionInProgress={isTestConnectionInProgress}
          isEditMode={isEditMode}
        />
      )}
      <FlexContainer>
        <FlexItem grow>
          {isEditMode && (
            <Button variant="danger" type="button" onClick={onDeleteClick} data-id="open-delete-modal">
              <FormattedMessage id={`tables.${formType}Delete`} />
            </Button>
          )}
        </FlexItem>
        {isEditMode && (
          <Button type="button" variant="secondary" disabled={isSubmitting || !dirty} onClick={onCancelClick}>
            <FormattedMessage id="form.cancel" />
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting || (isEditMode && !dirty)}>
          {isEditMode ? (
            <FormattedMessage id="form.saveChangesAndTest" />
          ) : (
            <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
          )}
        </Button>
      </FlexContainer>
    </>
  );
};
