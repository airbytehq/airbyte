import React from "react";

import FrequencyForm from "../../FrequencyForm";
import { SyncSchema } from "../../../core/resources/Schema";
import { IDataItem } from "../../DropDown/components/ListItem";
import { createFormErrorMessage } from "../../../utils/errorStatusMessage";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  errorStatus: number;
  schema: SyncSchema;
  additionBottomControls?: React.ReactNode;
  onSelectFrequency: (item: IDataItem) => void;
};

const CreateConnection: React.FC<IProps> = ({
  onSubmit,
  errorStatus,
  schema,
  onSelectFrequency,
  additionBottomControls
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

  const errorMessage = createFormErrorMessage(errorStatus);

  return (
    <FrequencyForm
      additionBottomControls={additionBottomControls}
      onDropDownSelect={onSelectFrequency}
      onSubmit={onSubmitForm}
      errorMessage={errorMessage}
      schema={schema}
    />
  );
};

export default CreateConnection;
