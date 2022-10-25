import { Formik } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { JobItem } from "components/JobItem/JobItem";
import { Card } from "components/ui/Card";

import { ServiceForm } from "views/Connector/ServiceForm";

import { useAdvancedModeSetting } from "../../../hooks/services/useAdvancedModeSetting";
import { generateMessageFromError } from "../../../utils/errorStatusMessage";
import { ConnectorServiceTypeControl } from "../ServiceForm/components/Controls/ConnectorServiceTypeControl";
import { FormControls } from "../ServiceForm/FormControls";
import { ServiceFormContextProvider } from "../ServiceForm/serviceFormContext";
import styles from "./ConnectorCard.module.scss";
import { useConnectorCardService } from "./hooks/useConnectorCardService";
import { ConnectorCardProps } from "./interfaces";
import { useTestConnector } from "./useTestConnector";

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
    formFields,
    getValues,
    initialValues,
    isFormSubmitting,
    job,
    jsonSchema,
    onFormSubmit,
    resetUiWidgetsInfo,
    saved,
    selectedConnectorDefinitionSpecificationId,
    setUiWidgetsInfo,
    uiWidgetsInfo,
    uniqueFormId,
    validationSchema,
  } = useConnectorCardService(props);
  const [advancedMode] = useAdvancedModeSetting();
  const { testConnector, isTestConnectionInProgress, onStopTesting, error } = useTestConnector(props);

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
                  formId={uniqueFormId}
                  jsonSchema={jsonSchema}
                  isTestConnectionInProgress={isTestConnectionInProgress}
                  formFields={formFields}
                  initialValues={initialValues}
                  validationSchema={validationSchema}
                  availableServices={availableServices}
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
            successMessage={
              props.successMessage || (saved && props.isEditMode && <FormattedMessage id="form.changesSaved" />)
            }
          />
        </div>
      </ServiceFormContextProvider>
    </Formik>
  );
};
