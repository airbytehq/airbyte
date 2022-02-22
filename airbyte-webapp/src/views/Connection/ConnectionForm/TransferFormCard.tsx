import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps } from "formik";
import * as yup from "yup";

import { ControlLabels, DropDown, DropDownRow } from "components";

import { useFrequencyDropdownData } from "./formConfig";
import { Connection, ScheduleProperties } from "core/resources/Connection";
import useConnection from "hooks/services/useConnectionHook";

import { FormCard } from "views/Connection/FormCard";

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

const TransferFormCard: React.FC<TransferFormProps> = ({ connection }) => {
  const { updateConnection } = useConnection();
  const formatMessage = useIntl().formatMessage;

  const onSubmit = async (values: { schedule: ScheduleProperties }) => {
    if (connection) {
      return await updateConnection({
        schedule: values.schedule,
        connectionId: connection.connectionId,
        namespaceDefinition: connection.namespaceDefinition,
        status: connection.status,
        prefix: connection.prefix,
        syncCatalog: connection.syncCatalog,
      });
    }

    return null;
  };

  const frequencies = useFrequencyDropdownData();

  return (
    <FormCard
      form={{
        initialValues: { schedule: connection?.schedule || null },
        validationSchema: transferFormValidationSchema,
        enableReinitialize: true,
        onSubmit,
      }}
      title={<FormattedMessage id="connection.transfer" />}
    >
      <Field name="schedule">
        {({ field, meta, form }: FieldProps<ScheduleProperties>) => (
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
              onChange={(item) => form.setFieldValue(field.name, item.value)}
            />
          </ConnectorLabel>
        )}
      </Field>
    </FormCard>
  );
};

export default TransferFormCard;
