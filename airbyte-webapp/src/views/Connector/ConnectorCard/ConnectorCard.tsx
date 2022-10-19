import { Formik } from "formik";
import { JSONSchema7 } from "json-schema";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

import { JobItem } from "components/JobItem/JobItem";
import { Card } from "components/ui/Card";

import {
  Connector,
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
  ConnectorT,
} from "core/domain/connector";
import { SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { ServiceForm, ServiceFormValues } from "views/Connector/ServiceForm";

import { isDestinationDefinitionSpecification } from "../../../core/domain/connector/destination";
import { isSourceDefinition, isSourceDefinitionSpecification } from "../../../core/domain/connector/source";
import { FormBaseItem, FormComponentOverrideProps } from "../../../core/form/types";
import { useFormChangeTrackerService, useUniqueFormId } from "../../../hooks/services/FormChangeTracker";
import { generateMessageFromError } from "../../../utils/errorStatusMessage";
import { useDocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorNameControl } from "../ServiceForm/components/Controls/ConnectorNameControl";
import { ConnectorServiceTypeControl } from "../ServiceForm/components/Controls/ConnectorServiceTypeControl";
import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgetsContext,
  useConstructValidationSchema,
} from "../ServiceForm/useBuildForm";
import styles from "./ConnectorCard.module.scss";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useTestConnector } from "./useTestConnector";

interface ConnectorCardProvidedPropsT {
  onServiceSelect?: (id: string) => void;
  fetchingConnectorError?: Error | null;
  formId?: string;
  onSubmit: (values: ServiceFormValues) => Promise<void> | void;
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  hasSuccess?: boolean;
  errorMessage?: React.ReactNode;
  isLoading?: boolean;
  formValues?: Partial<ServiceFormValues>;
  successMessage?: React.ReactNode;
}

interface ConnectorCardBaseProps extends ConnectorCardProvidedPropsT {
  title?: React.ReactNode;
  full?: boolean;
  jobInfo?: SynchronousJobRead | null;
  additionalSelectorComponent?: React.ReactNode;
}

interface ConnectorCardCreateProps extends ConnectorCardBaseProps {
  isEditMode?: false;
}

interface ConnectorCardEditProps extends ConnectorCardBaseProps {
  isEditMode: true;
  connector: ConnectorT;
}

export const ConnectorCard: React.FC<ConnectorCardCreateProps | ConnectorCardEditProps> = ({
  title,
  full,
  jobInfo,
  isLoading,
  onSubmit,
  additionalSelectorComponent,
  ...props
}) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const [advancedMode] = useAdvancedModeSetting();

  const { testConnector, isTestConnectionInProgress, onStopTesting, error, reset } = useTestConnector(props);
  const { trackTestConnectorFailure, trackTestConnectorSuccess, trackTestConnectorStarted } =
    useAnalyticsTrackFunctions(props.formType);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
    setErrorStatusRequest(null);
  }, [props.selectedConnectorDefinitionSpecification, reset]);

  const onHandleSubmit = async (values: ServiceFormValues) => {
    setErrorStatusRequest(null);
    setIsFormSubmitting(true);

    const connector = props.availableServices.find((item) => Connector.id(item) === values.serviceType);

    const testConnectorWithTracking = async () => {
      trackTestConnectorStarted(connector);
      try {
        await testConnector(values);
        trackTestConnectorSuccess(connector);
      } catch (e) {
        trackTestConnectorFailure(connector);
        throw e;
      }
    };

    try {
      await testConnectorWithTracking();
      onSubmit(values);
      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
      setIsFormSubmitting(false);
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  const { selectedConnectorDefinitionSpecification, onServiceSelect, availableServices, isEditMode } = props;
  const selectedConnectorDefinitionSpecificationId =
    selectedConnectorDefinitionSpecification && ConnectorSpecification.id(selectedConnectorDefinitionSpecification);

  const formId = useUniqueFormId(props.formId);
  const { clearFormChange } = useFormChangeTrackerService();

  const { formType, formValues } = props;

  const specifications = useBuildInitialSchema(selectedConnectorDefinitionSpecification);

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        serviceType: { type: "string" },
        ...(selectedConnectorDefinitionSpecification ? { name: { type: "string" } } : {}),
        ...Object.fromEntries(
          Object.entries({
            connectionConfiguration: isLoading ? null : specifications,
          }).filter(([, v]) => !!v)
        ),
      },
      required: ["name", "serviceType"],
    }),
    [isLoading, selectedConnectorDefinitionSpecification, specifications]
  );

  const { formFields, initialValues } = useBuildForm(jsonSchema, formValues);

  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();

  useEffect(() => {
    if (!selectedConnectorDefinitionSpecification) {
      return;
    }

    const selectedServiceDefinition = availableServices.find((service) => {
      if (isSourceDefinition(service)) {
        const serviceDefinitionId = service.sourceDefinitionId;
        return (
          isSourceDefinitionSpecification(selectedConnectorDefinitionSpecification) &&
          serviceDefinitionId === selectedConnectorDefinitionSpecification.sourceDefinitionId
        );
      }
      const serviceDefinitionId = service.destinationDefinitionId;
      return (
        isDestinationDefinitionSpecification(selectedConnectorDefinitionSpecification) &&
        serviceDefinitionId === selectedConnectorDefinitionSpecification.destinationDefinitionId
      );
    });
    setDocumentationUrl(selectedServiceDefinition?.documentationUrl ?? "");
    setDocumentationPanelOpen(true);
  }, [availableServices, selectedConnectorDefinitionSpecification, setDocumentationPanelOpen, setDocumentationUrl]);

  const uiOverrides = useMemo(() => {
    return {
      name: {
        component: (property: FormBaseItem, componentProps: FormComponentOverrideProps) => (
          <ConnectorNameControl property={property} formType={formType} {...componentProps} />
        ),
      },
      serviceType: {
        /* since we use <ConnectorServiceTypeControl/> outside formik form
           we need to keep the serviceType field in formik, but hide it.
           serviceType prop will be removed in further PR
        */
        component: () => null,
      },
    };
  }, [formType]);

  const { uiWidgetsInfo, setUiWidgetsInfo, resetUiWidgetsInfo } = useBuildUiWidgetsContext(
    formFields,
    initialValues,
    uiOverrides
  );

  const validationSchema = useConstructValidationSchema(jsonSchema, uiWidgetsInfo);

  const getValues = useCallback(
    (values: ServiceFormValues) =>
      validationSchema.cast(values, {
        stripUnknown: true,
      }),
    [validationSchema]
  );

  const onFormSubmit = useCallback(
    async (values: ServiceFormValues) => {
      const valuesToSend = getValues(values);
      await onSubmit(valuesToSend);

      clearFormChange(formId);
    },
    [clearFormChange, formId, getValues, onSubmit]
  );

  return (
    <Formik
      validateOnBlur
      validateOnChange
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onFormSubmit}
      enableReinitialize
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
                formId={formId}
                jsonSchema={jsonSchema}
                errorMessage={props.errorMessage || (error && generateMessageFromError(error))}
                isTestConnectionInProgress={isTestConnectionInProgress}
                onStopTesting={onStopTesting}
                testConnector={testConnector}
                onSubmit={onHandleSubmit}
                getValues={getValues}
                resetUiWidgetsInfo={resetUiWidgetsInfo}
                setUiWidgetsInfo={setUiWidgetsInfo}
                uiWidgetsInfo={uiWidgetsInfo}
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
      </div>
    </Formik>
  );
};
