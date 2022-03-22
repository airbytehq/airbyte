import React from "react";
import { Form, useFormikContext } from "formik";
import styled from "styled-components";

import { Spinner } from "components";

import { FormBlock } from "core/form/types";
import { ServiceFormValues } from "./types";
import { useServiceForm } from "./serviceFormContext";

import { FormSection } from "./components/Sections/FormSection";
import ShowLoadingMessage from "./components/ShowLoadingMessage";
import EditControls from "./components/EditControls";
import CreateControls from "./components/CreateControls";

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

const FormRoot: React.FC<{
  formFields: FormBlock;
  hasSuccess?: boolean;
  isTestConnectionInProgress: boolean;
  errorMessage?: React.ReactNode;
  fetchingConnectorError?: Error | null;
  successMessage?: React.ReactNode;
  onRetest?: () => void;
}> = ({
  isTestConnectionInProgress,
  onRetest,
  formFields,
  successMessage,
  errorMessage,
  fetchingConnectorError,
  hasSuccess,
}) => {
  const {
    resetForm,
    dirty,
    isSubmitting,
    isValid,
  } = useFormikContext<ServiceFormValues>();

  const {
    resetUiFormProgress,
    isLoadingSchema,
    selectedService,
    isEditMode,
    formType,
  } = useServiceForm();

  return (
    <FormContainer>
      <FormSection blocks={formFields} />
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
          isSubmitting={isSubmitting}
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
          isSubmitting={isSubmitting}
          errorMessage={errorMessage}
          formType={formType}
          isLoadSchema={isLoadingSchema}
          fetchingConnectorError={fetchingConnectorError}
          hasSuccess={hasSuccess}
        />
      )}
    </FormContainer>
  );
};

export { FormRoot };
