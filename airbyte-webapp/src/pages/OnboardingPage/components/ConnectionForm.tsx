import React from "react";
import { useResource } from "rest-hooks";

import FrequencyForm from "../../../components/FrequencyForm";
import SchemaResource, { SyncSchema } from "../../../core/resources/Schema";
import {
  constructInitialSchemaState,
  constructNewSchema
} from "../../../core/helpers";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  errorMessage?: React.ReactNode;
  sourceImplementationId: string;
};

const ConnectionStep: React.FC<IProps> = ({
  onSubmit,
  errorMessage,
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
      errorMessage={errorMessage}
      schema={formSyncSchema}
      initialCheckedSchema={initialChecked}
    />
  );
};

export default ConnectionStep;
