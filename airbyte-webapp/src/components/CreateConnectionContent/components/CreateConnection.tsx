import React from "react";
import { FormattedMessage } from "react-intl";

import FrequencyForm from "../../FrequencyForm";
import { SyncSchema } from "../../../core/resources/Schema";
import { IDataItem } from "../../DropDown/components/ListItem";
import {
  constructInitialSchemaState,
  constructNewSchema
} from "../../../core/helpers";

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
  const {
    formSyncSchema,
    initialChecked,
    allSchemaChecked,
    syncModeInitialState
  } = constructInitialSchemaState(schema);

  const onSubmitForm = async (
    values: { frequency: string },
    checkedState: string[]
  ) => {
    const newSchema = constructNewSchema(schema, checkedState);
    await onSubmit({ ...values, syncSchema: newSchema });
  };

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );

  return (
    <FrequencyForm
      syncModeInitialState={syncModeInitialState}
      allSchemaChecked={allSchemaChecked}
      onDropDownSelect={onSelectFrequency}
      onSubmit={onSubmitForm}
      errorMessage={errorMessage}
      schema={formSyncSchema}
      initialCheckedSchema={initialChecked}
    />
  );
};

export default CreateConnection;
