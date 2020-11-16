import React from "react";
import { useResource } from "rest-hooks";

import FrequencyForm from "../../../../../components/FrequencyForm";
import SchemaResource, {
  SyncSchema
} from "../../../../../core/resources/Schema";
import { IDataItem } from "../../../../../components/DropDown/components/ListItem";
import {
  constructInitialSchemaState,
  constructNewSchema
} from "../../../../../core/helpers";
import { FormattedMessage } from "react-intl";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  errorStatus: number;
  sourceId: string;
  onSelectFrequency: (item: IDataItem) => void;
};

const CreateConnection: React.FC<IProps> = ({
  onSubmit,
  errorStatus,
  sourceId,
  onSelectFrequency
}) => {
  const { schema } = useResource(SchemaResource.schemaShape(), {
    sourceId
  });

  const {
    formSyncSchema,
    initialChecked,
    allSchemaChecked
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
