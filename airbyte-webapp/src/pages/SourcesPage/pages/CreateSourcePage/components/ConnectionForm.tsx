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

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  sourceImplementationId: string;
};

const ConnectionStep: React.FC<IProps> = ({
  onSubmit,
  sourceImplementationId
}) => {
  const { schema } = useResource(SchemaResource.schemaShape(), {
    sourceImplementationId
  });

  const { formSyncSchema, initialChecked } = constructInitialSchemaState(
    schema
  );

  const onSubmitForm = async (
    values: { frequency: string },
    checkedState: string[]
  ) => {
    const newSchema = constructNewSchema(schema, checkedState);
    await onSubmit({ ...values, syncSchema: newSchema });
  };

  return (
    <FrequencyForm
      onSubmit={onSubmitForm}
      schema={formSyncSchema}
      initialCheckedSchema={initialChecked}
    />
  );
};

export default ConnectionStep;
