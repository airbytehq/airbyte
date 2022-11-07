import { Form, useFormikContext } from "formik";
import React from "react";

import { Spinner } from "components/ui/Spinner";

import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { FormBlock } from "core/form/types";

import CreateControls from "./components/CreateControls";
import EditControls from "./components/EditControls";
import { FormSection } from "./components/Sections/FormSection";
import ShowLoadingMessage from "./components/ShowLoadingMessage";
import { useConnectorForm } from "./connectorFormContext";
import styles from "./FormRoot.module.scss";
import { ConnectorFormValues } from "./types";

interface FormRootProps {
  formFields: FormBlock;
  hasSuccess?: boolean;
  isTestConnectionInProgress?: boolean;
  errorMessage?: React.ReactNode;
  fetchingConnectorError?: Error | null;
  successMessage?: React.ReactNode;
  onRetest?: () => void;
  onStopTestingConnector?: () => void;
  selectedConnector: ConnectorDefinitionSpecification | undefined;
}

export const FormRoot: React.FC<FormRootProps> = ({
  isTestConnectionInProgress = false,
  onRetest,
  formFields,
  successMessage,
  errorMessage,
  fetchingConnectorError,
  hasSuccess,
  onStopTestingConnector,
  selectedConnector,
}) => {
  const { dirty, isSubmitting, isValid } = useFormikContext<ConnectorFormValues>();
  const { resetConnectorForm, isLoadingSchema, selectedService, isEditMode, formType } = useConnectorForm();

  return (
    <Form>
      <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
      {isLoadingSchema && (
        <div className={styles.loaderContainer}>
          <Spinner />
          <div className={styles.loadingMessage}>
            <ShowLoadingMessage connector={selectedService?.name} />
          </div>
        </div>
      )}

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
    </Form>
  );
};
