import { Form, useFormikContext } from "formik";
import React from "react";
import styled from "styled-components";

import { Spinner } from "components";
import { DefinitioDetails } from "components/ConnectorBlocks";

import { FormBlock } from "core/form/types";

import CreateControls from "./components/CreateControls";
// import EditControls from "./components/EditControls";
import { FormSection } from "./components/Sections/FormSection";
import ShowLoadingMessage from "./components/ShowLoadingMessage";
import { useServiceForm } from "./serviceFormContext";
import { ServiceFormValues } from "./types";

const FormContainer = styled(Form)`
  //padding: 22px 27px 23px 24px;
  // padding: 34px 40px 34px 80px;
`;

const LoaderContainer = styled.div`
  text-align: center;
  padding: 22px 0 23px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const LoadingMessage = styled.div`
  margin-left: 14px;
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
  isCopyMode?: boolean;
  onBack?: () => void;
}

const FormRoot: React.FC<FormRootProps> = ({
  isTestConnectionInProgress = false,
  // onRetest,
  formFields,
  // successMessage,
  errorMessage,
  fetchingConnectorError,
  hasSuccess,
  isCopyMode,
  onStopTestingConnector,
  onBack,
}) => {
  const { dirty, isSubmitting, isValid } = useFormikContext<ServiceFormValues>();
  const { isLoadingSchema, selectedService, isEditMode, formType } = useServiceForm(); // resetServiceForm

  return (
    <FormContainer>
      {!isEditMode && <DefinitioDetails name={selectedService?.name} icon={selectedService?.icon} type={formType} />}
      <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
      {isLoadingSchema && (
        <LoaderContainer>
          <Spinner />
          <LoadingMessage>
            <ShowLoadingMessage connector={selectedService?.name} />
          </LoadingMessage>
        </LoaderContainer>
      )}
      {/* {isEditMode ? (
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
            resetServiceForm();
          }}
          successMessage={successMessage}
        />
      ) : ( */}
      {!isLoadingSchema && (
        <CreateControls
          isTestConnectionInProgress={isTestConnectionInProgress}
          onCancelTesting={onStopTestingConnector}
          isSubmitting={isSubmitting || isTestConnectionInProgress}
          errorMessage={errorMessage}
          formType={formType}
          isLoadSchema={isLoadingSchema}
          fetchingConnectorError={fetchingConnectorError}
          hasSuccess={hasSuccess}
          disabled={isEditMode || isCopyMode ? !isValid : !(isValid && dirty)}
          onBack={onBack}
        />
      )}

      {/* )} */}
    </FormContainer>
  );
};

export { FormRoot };
