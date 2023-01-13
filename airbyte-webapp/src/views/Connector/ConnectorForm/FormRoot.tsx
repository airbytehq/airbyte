import { Form, useFormikContext } from "formik";
import React from "react";

import { FormBlock } from "core/form/types";

import CreateControls from "./components/CreateControls";
import EditControls from "./components/EditControls";
import { FormSection } from "./components/Sections/FormSection";
import { useConnectorForm } from "./connectorFormContext";
import { ConnectorFormValues } from "./types";

interface FormRootProps {
  formFields: FormBlock;
  hasSuccess?: boolean;
  isTestConnectionInProgress?: boolean;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  onRetest?: () => void;
  onStopTestingConnector?: () => void;
}

export const FormRoot: React.FC<FormRootProps> = ({
  isTestConnectionInProgress = false,
  onRetest,
  formFields,
  successMessage,
  errorMessage,
  hasSuccess,
  onStopTestingConnector,
}) => {
  const { dirty, isSubmitting, isValid } = useFormikContext<ConnectorFormValues>();
  const { resetConnectorForm, isEditMode, formType } = useConnectorForm();

  return (
    <Form>
      <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
      {isEditMode ? (
        <EditControls
          isTestConnectionInProgress={isTestConnectionInProgress}
          onCancelTesting={onStopTestingConnector}
          isSubmitting={isSubmitting || isTestConnectionInProgress}
          errorMessage={errorMessage}
          formType={formType}
          onRetestClick={onRetest}
          isValid={isValid}
          dirty={dirty}
          onCancelClick={() => {
            resetConnectorForm();
          }}
          successMessage={successMessage}
        />
      ) : (
        <CreateControls
          isTestConnectionInProgress={isTestConnectionInProgress}
          onCancelTesting={onStopTestingConnector}
          isSubmitting={isSubmitting || isTestConnectionInProgress}
          errorMessage={errorMessage}
          formType={formType}
          hasSuccess={hasSuccess}
        />
      )}
    </Form>
  );
};
