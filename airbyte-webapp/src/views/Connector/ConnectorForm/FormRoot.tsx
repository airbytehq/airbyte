import { Form, useFormikContext } from "formik";
import React from "react";

import { Card } from "components/ui/Card";
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
  onDelete?: () => Promise<void>;
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
  onDelete,
  selectedConnector,
}) => {
  const { dirty, isSubmitting, isValid } = useFormikContext<ConnectorFormValues>();
  const { resetConnectorForm, isLoadingSchema, selectedConnectorDefinition, isEditMode, formType } = useConnectorForm();

  return (
    <Form>
      <Card className={styles.cardContainer}>
        <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
        {isLoadingSchema && (
          <div className={styles.loaderContainer}>
            <Spinner />
            <div className={styles.loadingMessage}>
              <ShowLoadingMessage connector={selectedConnectorDefinition?.name} />
            </div>
          </div>
        )}
      </Card>

      {isEditMode ? (
        <EditControls
          onDelete={onDelete}
          isTestConnectionInProgress={isTestConnectionInProgress}
          onCancelTesting={onStopTestingConnector}
          isSubmitting={isSubmitting || isTestConnectionInProgress}
          errorMessage={errorMessage}
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
