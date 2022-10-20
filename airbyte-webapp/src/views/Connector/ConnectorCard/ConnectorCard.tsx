import { Formik } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { JobItem } from "components/JobItem/JobItem";
import { Card } from "components/ui/Card";

import { ServiceForm } from "views/Connector/ServiceForm";

import { generateMessageFromError } from "../../../utils/errorStatusMessage";
import { ConnectorServiceTypeControl } from "../ServiceForm/components/Controls/ConnectorServiceTypeControl";
import { FormControls } from "../ServiceForm/FormControls";
import { ServiceFormContextProvider } from "../ServiceForm/serviceFormContext";
import styles from "./ConnectorCard.module.scss";
import { ConnectorCardProps } from "./interfaces";
import { useConnectorCardService } from "./useConnectorCardService";

export const ConnectorCard: React.FC<ConnectorCardProps> = (props) => {
  const {
    title,
    full,
    isLoading,
    additionalSelectorComponent,
    formType,
    selectedConnectorDefinitionSpecification,
    isEditMode,
    availableServices,
    onServiceSelect,
    onDelete,
  } = props;
  const {
    advancedMode,
    error,
    formFields,
    getValues,
    initialValues,
    isFormSubmitting,
    isTestConnectionInProgress,
    job,
    jsonSchema,
    onFormSubmit,
    onHandleSubmit,
    onStopTesting,
    resetUiWidgetsInfo,
    saved,
    selectedConnectorDefinitionSpecificationId,
    setUiWidgetsInfo,
    testConnector,
    uiWidgetsInfo,
    uniqueFormId,
    validationSchema,
  } = useConnectorCardService(props);

  return (
    <Formik
      validateOnBlur
      validateOnChange
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onFormSubmit}
      enableReinitialize
    >
      <ServiceFormContextProvider
        widgetsInfo={uiWidgetsInfo}
        getValues={getValues}
        setUiWidgetsInfo={setUiWidgetsInfo}
        resetUiWidgetsInfo={resetUiWidgetsInfo}
        formType={formType}
        selectedConnector={selectedConnectorDefinitionSpecification}
        availableServices={availableServices}
        isEditMode={isEditMode}
        isLoadingSchema={isLoading}
        validationSchema={validationSchema}
      >
        <div>
          <Card title={title} fullWidth={full}>
            <div className={styles.cardForm}>
              <div className={styles.connectorSelectControl}>
                <ConnectorServiceTypeControl
                  formType={props.formType}
                  onChangeServiceType={onServiceSelect}
                  availableServices={availableServices}
                  isEditMode={isEditMode}
                  selectedServiceId={selectedConnectorDefinitionSpecificationId}
                  disabled={isFormSubmitting}
                />
              </div>
              {additionalSelectorComponent}
              <div>
                <ServiceForm
                  {...props}
                  formId={uniqueFormId}
                  jsonSchema={jsonSchema}
                  isTestConnectionInProgress={isTestConnectionInProgress}
                  onSubmit={onHandleSubmit}
                  formFields={formFields}
                  initialValues={initialValues}
                  validationSchema={validationSchema}
                  successMessage={
                    props.successMessage || (saved && props.isEditMode && <FormattedMessage id="form.changesSaved" />)
                  }
                />
                {/* Show the job log only if advanced mode is turned on or the actual job failed (not the check inside the job) */}
                {job && (advancedMode || !job.succeeded) && <JobItem job={job} />}
              </div>
            </div>
          </Card>
          <FormControls
            onDelete={onDelete}
            errorMessage={props.errorMessage || (error && generateMessageFromError(error))}
            isTestConnectionInProgress={isTestConnectionInProgress}
            onStopTestingConnector={onStopTesting ? () => onStopTesting() : undefined}
            onRetest={testConnector ? async () => await testConnector() : undefined}
            formFields={formFields}
            selectedConnector={selectedConnectorDefinitionSpecification}
          />
        </div>
      </ServiceFormContextProvider>
    </Formik>
  );
};
