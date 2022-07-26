import { Form, useFormikContext } from "formik";
import React from "react";
import styled from "styled-components";

import { Spinner } from "components";

import { FormBlock } from "core/form/types";

import CreateControls from "./components/CreateControls";
import EditControls from "./components/EditControls";
import { FormSection } from "./components/Sections/FormSection";
import ShowLoadingMessage from "./components/ShowLoadingMessage";
import { useServiceForm } from "./serviceFormContext";
import { ServiceFormValues } from "./types";

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const LoaderContainer = styled.div`
  text-align: center;
  padding: 22px 0 23px;
`;

const LoadingMessage = styled.div`
  margin-top: 10px;
`;

interface FormRootProps {
  formFields: FormBlock;
  hasSuccess?: boolean;
  isTestConnectionInProgress?: boolean;
  errorMessage?: React.ReactNode;
  fetchingConnectorError?: Error | null;
  successMessage?: React.ReactNode;
  onRetest?: () => void;
  onStopTestingConnector?: () => void;
}

const FormRoot: React.FC<FormRootProps> = ({
  isTestConnectionInProgress = false,
  onRetest,
  formFields,
  successMessage,
  errorMessage,
  fetchingConnectorError,
  hasSuccess,
  onStopTestingConnector,
}) => {
  const { resetForm, dirty, isSubmitting, isValid } = useFormikContext<ServiceFormValues>();

  const { resetUiFormProgress, isLoadingSchema, selectedService, isEditMode, formType } = useServiceForm();

  return (
    <FormContainer>
      <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
      {isLoadingSchema && (
        <LoaderContainer>
          <Spinner />
          <LoadingMessage>
            <ShowLoadingMessage connector={selectedService?.name} />
          </LoadingMessage>
        </LoaderContainer>
      )}

      {isEditMode ? (
        <EditControls
          isTestConnectionInProgress={isTestConnectionInProgress}
          onCancelTesting={onStopTestingConnector}
          isSubmitting={isSubmitting || isTestConnectionInProgress}
          errorMessage={errorMessage}
          formType={formType}
          onRetest={onRetest}
          isValid={isValid}
          dirty={dirty}
          resetForm={() => {
            resetForm();
            resetUiFormProgress();
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
          isLoadSchema={isLoadingSchema}
          fetchingConnectorError={fetchingConnectorError}
          hasSuccess={hasSuccess}
          isValid={isValid}
        />
      )}
    </FormContainer>
  );
};

export { FormRoot };
