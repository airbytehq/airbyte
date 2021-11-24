import React, { useCallback, useState } from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Form, Formik } from "formik";
import * as yup from "yup";

import { ControlLabels, DropDown, DropDownRow } from "components";

import { useFrequencyDropdownData } from "./formConfig";
import { Connection, ScheduleProperties } from "core/resources/Connection";
import EditControls from "./components/EditControls";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import useConnection from "hooks/services/useConnectionHook";

const FormContainer = styled(Form)`
  padding: 22px 27px 15px 24px;
`;

const ConnectorLabel = styled(ControlLabels)`
  max-width: 328px;
  margin-right: 20px;
  vertical-align: top;
`;

type TransferFormProps = {
  className?: string;
  onDropDownSelect?: (item: DropDownRow.IDataItem) => void;
  connection?: Connection;
};

const transferFormValidationSchema = yup.object({
  schedule: yup
    .object({
      units: yup.number().required("form.empty.error"),
      timeUnit: yup.string().required("form.empty.error"),
    })
    .nullable()
    .defined("form.empty.error"),
});

const TransferForm: React.FC<TransferFormProps> = ({
  className,
  connection,
}) => {
  const { updateConnection } = useConnection();

  const [submitError, setSubmitError] = useState<Error | null>(null);
  const [saved, setSaved] = useState<boolean>(false);
  const formatMessage = useIntl().formatMessage;

  const onFormSubmit = useCallback(
    async (values: { schedule: ScheduleProperties | null }) => {
      setSubmitError(null);
      setSaved(false);

      try {
        if (connection) {
          await updateConnection({
            schedule: values.schedule,
            connectionId: connection.connectionId,
            namespaceDefinition: connection.namespaceDefinition,
            status: connection.status,
            prefix: connection.prefix,
            syncCatalog: connection.syncCatalog,
          });
        }
        setSaved(true);
      } catch (e) {
        setSubmitError(e);
      }
    },
    [updateConnection, connection]
  );

  const errorMessage = submitError ? createFormErrorMessage(submitError) : null;
  const frequencies = useFrequencyDropdownData();
  const initialValues = { schedule: connection?.schedule || null };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={transferFormValidationSchema}
      enableReinitialize={true}
      onSubmit={onFormSubmit}
    >
      {({ setFieldValue, isSubmitting, dirty, resetForm, isValid }) => (
        <FormContainer className={className}>
          <Field name="schedule">
            {({ field, meta }: FieldProps<ScheduleProperties>) => (
              <ConnectorLabel
                error={!!meta.error && meta.touched}
                label={formatMessage({
                  id: "connection.replicationFrequency",
                })}
                nextLine
                message={formatMessage({
                  id: "connection.replicationFrequency.subtitle",
                })}
              >
                <DropDown
                  {...field}
                  error={!!meta.error && meta.touched}
                  options={frequencies}
                  onChange={(item) => {
                    setFieldValue(field.name, item.value);
                    setSaved(false);
                  }}
                />
              </ConnectorLabel>
            )}
          </Field>
          <EditControls
            withLine
            isSubmitting={isSubmitting}
            dirty={dirty}
            resetForm={resetForm}
            successMessage={
              saved && formatMessage({ id: "settings.changeSaved" })
            }
            errorMessage={
              errorMessage || !isValid
                ? formatMessage({ id: "connectionForm.validation.error" })
                : null
            }
          />
        </FormContainer>
      )}
    </Formik>
  );
};

export default TransferForm;
