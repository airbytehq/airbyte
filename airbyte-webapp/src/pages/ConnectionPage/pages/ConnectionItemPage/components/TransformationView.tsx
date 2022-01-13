import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Field, FieldArray } from "formik";

import { NormalizationField } from "views/Connection/ConnectionForm/components/NormalizationField";
import { TransformationField } from "views/Connection/ConnectionForm/components/TransformationField";
import {
  getInitialNormalization,
  getInitialTransformations,
  mapFormPropsToOperation,
  useDefaultTransformation,
} from "views/Connection/ConnectionForm/formConfig";
import { FormCard } from "views/Connection/FormCard";
import {
  Connection,
  NormalizationType,
  Operation,
  OperatorType,
  Transformation,
} from "core/domain/connection";
import useConnection from "hooks/services/useConnectionHook";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useDestinationDefinitionSpecificationLoadAsync } from "hooks/services/useDestinationHook";

type TransformationViewProps = {
  connection: Connection;
};

const Content = styled.div`
  max-width: 1073px;
  margin: 0 auto;
  padding-bottom: 10px;
`;

const CustomTransformationsCard: React.FC<{
  operations: Operation[];
  onSubmit: (newValue: { transformations?: Transformation[] }) => void;
}> = ({ operations, onSubmit }) => {
  const defaultTransformation = useDefaultTransformation();

  const initialValues = useMemo(
    () => ({
      transformations: getInitialTransformations(operations),
    }),
    [operations]
  );

  return (
    <FormCard
      title={<FormattedMessage id="connection.customTransformations" />}
      collapsible
      bottomSeparator
      form={{
        initialValues,
        enableReinitialize: true,
        onSubmit,
      }}
    >
      <FieldArray name="transformations">
        {(formProps) => (
          <TransformationField
            defaultTransformation={defaultTransformation}
            {...formProps}
          />
        )}
      </FieldArray>
    </FormCard>
  );
};

const NormalizationCard: React.FC<{
  operations: Operation[];
  onSubmit: (newValue: { normalization?: NormalizationType }) => void;
}> = ({ operations, onSubmit }) => {
  const initialValues = useMemo(
    () => ({
      normalization: getInitialNormalization(operations, true),
    }),
    [operations]
  );
  return (
    <FormCard
      form={{
        initialValues,
        onSubmit,
      }}
      title={<FormattedMessage id="connection.normalization" />}
      collapsible
    >
      <Field name="normalization" component={NormalizationField} />
    </FormCard>
  );
};

const TransformationView: React.FC<TransformationViewProps> = ({
  connection,
}) => {
  const definition = useDestinationDefinitionSpecificationLoadAsync(
    connection.destination.destinationDefinitionId
  );
  const { updateConnection } = useConnection();
  const workspace = useCurrentWorkspace();

  const onSubmit = async (values: {
    transformations?: Transformation[];
    normalization?: NormalizationType;
  }) => {
    const newOp = mapFormPropsToOperation(
      values,
      connection.operations,
      workspace.workspaceId
    );

    const operations = values.transformations
      ? connection.operations
          .filter(
            (op) =>
              op.operatorConfiguration.operatorType ===
              OperatorType.Normalization
          )
          .concat(newOp)
      : newOp.concat(
          connection.operations.filter(
            (op) => op.operatorConfiguration.operatorType === OperatorType.Dbt
          )
        );

    return updateConnection({
      namespaceDefinition: connection.namespaceDefinition,
      namespaceFormat: connection.namespaceFormat,
      prefix: connection.prefix,
      schedule: connection.schedule,
      syncCatalog: connection.syncCatalog,
      connectionId: connection.connectionId,
      status: connection.status,
      operations: operations,
    });
  };

  return (
    <Content>
      {definition.supportsNormalization && (
        <NormalizationCard
          operations={connection.operations}
          onSubmit={onSubmit}
        />
      )}
      {definition.supportsDbt && (
        <CustomTransformationsCard
          operations={connection.operations}
          onSubmit={onSubmit}
        />
      )}
    </Content>
  );
};

export default TransformationView;
