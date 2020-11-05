import React from "react";
import { useResource } from "rest-hooks";

import FrequencyForm from "../../../../../components/FrequencyForm";
import SchemaResource, {
  SyncSchema
} from "../../../../../core/resources/Schema";
import {
  constructInitialSchemaState,
  constructNewSchema
} from "../../../../../core/helpers";
import { IDataItem } from "../../../../../components/DropDown/components/ListItem";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  sourceId: string;
  onSelectFrequency: (item: IDataItem) => void;
};

const ConnectionForm: React.FC<IProps> = ({
  onSubmit,
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

  return (
    <FrequencyForm
      allSchemaChecked={allSchemaChecked}
      onSubmit={onSubmitForm}
      schema={formSyncSchema}
      initialCheckedSchema={initialChecked}
      onDropDownSelect={onSelectFrequency}
    />
  );
};

export default ConnectionForm;
