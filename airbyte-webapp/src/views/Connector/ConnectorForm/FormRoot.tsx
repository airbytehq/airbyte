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
  connectionTestSuccess?: boolean;
  isTestConnectionInProgress?: boolean;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  onRetest?: () => void;
  onStopTestingConnector?: () => void;
  submitLabel?: string;
  footerClassName?: string;
  bodyClassName?: string;
  /**
   * Called in case the user cancels the form - if not provided, no cancel button is rendered
   */
  onCancel?: () => void;
  /**
   * Called in case the user reset the form - if not provided, no reset button is rendered
   */
  onReset?: () => void;
}

export const FormRoot: React.FC<FormRootProps> = ({
  isTestConnectionInProgress = false,
  onRetest,
  formFields,
  successMessage,
  errorMessage,
  connectionTestSuccess,
  onStopTestingConnector,
  submitLabel,
  footerClassName,
  bodyClassName,
  onCancel,
  onReset,
}) => {
  const { dirty, isSubmitting, isValid } = useFormikContext<ConnectorFormValues>();
  const { resetConnectorForm, isEditMode, formType } = useConnectorForm();

  return (
    <Form>
      <div className={bodyClassName}>
        <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
      </div>
      <div className={footerClassName}>
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
            submitLabel={submitLabel}
            onCancel={onCancel}
            onReset={onReset}
            connectionTestSuccess={connectionTestSuccess}
          />
        )}
      </div>
    </Form>
  );
};
