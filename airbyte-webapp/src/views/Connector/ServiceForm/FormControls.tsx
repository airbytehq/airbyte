import { useFormikContext } from "formik";
import React from "react";

import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { FormBlock } from "core/form/types";

import CreateControls from "./components/CreateControls";
import EditControls from "./components/EditControls";
import { useServiceForm } from "./serviceFormContext";
import { ServiceFormValues } from "./types";

interface FormControlsProps {
  formFields: FormBlock;
  hasSuccess?: boolean;
  isTestConnectionInProgress?: boolean;
  errorMessage?: React.ReactNode;
  fetchingConnectorError?: Error | null;
  successMessage?: React.ReactNode;
  onRetest?: () => void;
  onStopTestingConnector?: () => void;
  onDelete?: () => Promise<unknown>;
  selectedConnector: ConnectorDefinitionSpecification | undefined;
}

export const FormControls: React.FC<FormControlsProps> = ({
  onDelete,
  isTestConnectionInProgress = false,
  onRetest,
  successMessage,
  errorMessage,
  fetchingConnectorError,
  hasSuccess,
  onStopTestingConnector,
  selectedConnector,
}) => {
  const { dirty, isSubmitting, isValid } = useFormikContext<ServiceFormValues>();
  const { resetServiceForm, isLoadingSchema, isEditMode, formType } = useServiceForm();

  return (
    <>
      {isEditMode ? (
        <EditControls
          onDelete={onDelete}
          isTestConnectionInProgress={isTestConnectionInProgress}
          onCancelTesting={onStopTestingConnector}
          isSubmitting={isSubmitting || isTestConnectionInProgress}
          errorMessage={errorMessage}
          formType={formType}
          onRetestClick={onRetest}
          isValid={isValid}
          dirty={dirty}
          onCancelClick={() => {
            resetServiceForm();
          }}
          successMessage={successMessage}
        />
      ) : (
        selectedConnector && (
          <CreateControls
            isTestConnectionInProgress={isTestConnectionInProgress}
            onCancelTesting={onStopTestingConnector}
            isSubmitting={isSubmitting || isTestConnectionInProgress}
            errorMessage={errorMessage}
            formType={formType}
            isLoadSchema={isLoadingSchema}
            fetchingConnectorError={fetchingConnectorError}
            hasSuccess={hasSuccess}
          />
        )
      )}
    </>
  );
};
