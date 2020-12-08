import React from "react";
import { FormattedMessage } from "react-intl";

import FrequencyForm from "../../FrequencyForm";
import { SyncSchema } from "../../../core/resources/Schema";
import { IDataItem } from "../../DropDown/components/ListItem";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  errorStatus: number;
  schema: SyncSchema;
  onSelectFrequency: (item: IDataItem) => void;
};

const CreateConnection: React.FC<IProps> = ({
  onSubmit,
  errorStatus,
  schema,
  onSelectFrequency
}) => {
  const onSubmitForm = async (values: {
    frequency: string;
    schema: SyncSchema;
  }) => {
    await onSubmit({
      frequency: values.frequency,
      syncSchema: values.schema
    });
  };

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );

  return (
    <FrequencyForm
      onDropDownSelect={onSelectFrequency}
      onSubmit={onSubmitForm}
      errorMessage={errorMessage}
      schema={schema}
    />
  );
};

export default CreateConnection;
