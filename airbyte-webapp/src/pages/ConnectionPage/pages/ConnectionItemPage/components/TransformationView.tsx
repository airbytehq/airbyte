import { Field, FieldArray } from "formik";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard, H4 } from "components";

import {
  Connection,
  ConnectionStatus,
  NormalizationType,
  Operation,
  OperatorType,
  Transformation,
} from "core/domain/connection";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import { useUpdateConnection } from "hooks/services/useConnectionHook";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { FormikOnSubmit } from "types/formik";
import { NormalizationField } from "views/Connection/ConnectionForm/components/NormalizationField";
import { TransformationField } from "views/Connection/ConnectionForm/components/TransformationField";
import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";
import {
  getInitialNormalization,
  getInitialTransformations,
  mapFormPropsToOperation,
  useDefaultTransformation,
} from "views/Connection/ConnectionForm/formConfig";
import { FormCard } from "views/Connection/FormCard";

interface TransformationViewProps {
  connection: Connection;
}

const Content = styled.div`
  max-width: 1073px;
  margin: 0 auto;
  padding-bottom: 10px;
`;

const NoSupportedTransformationCard = styled(ContentCard)`
  max-width: 500px;
  margin: 0 auto;
  min-height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const CustomTransformationsCard: React.FC<{
  operations: Operation[];
  onSubmit: FormikOnSubmit<{ transformations?: Transformation[] }>;
  mode: ConnectionFormMode;
}> = ({ operations, onSubmit, mode }) => {
  const defaultTransformation = useDefaultTransformation();

  const initialValues = useMemo(
    () => ({
      transformations: getInitialTransformations(operations),
    }),
    [operations]
  );

  return (
    <FormCard<{ transformations?: Transformation[] }>
      title={<FormattedMessage id="connection.customTransformations" />}
      collapsible
      bottomSeparator
      form={{
        initialValues,
        enableReinitialize: true,
        onSubmit,
      }}
      mode={mode}
    >
      <FieldArray name="transformations">
        {(formProps) => (
          <TransformationField defaultTransformation={defaultTransformation} {...formProps} mode={mode} />
        )}
      </FieldArray>
    </FormCard>
  );
};

const NormalizationCard: React.FC<{
  operations: Operation[];
  onSubmit: FormikOnSubmit<{ normalization?: NormalizationType }>;
  mode: ConnectionFormMode;
}> = ({ operations, onSubmit, mode }) => {
  const initialValues = useMemo(
    () => ({
      normalization: getInitialNormalization(operations, true),
    }),
    [operations]
  );

  return (
    <FormCard<{ normalization?: NormalizationType }>
      form={{
        initialValues,
        onSubmit,
      }}
      title={<FormattedMessage id="connection.normalization" />}
      collapsible
      mode={mode}
    >
      <Field name="normalization" component={NormalizationField} mode={mode} />
    </FormCard>
  );
};

const TransformationView: React.FC<TransformationViewProps> = ({ connection }) => {
  const definition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const { mutateAsync: updateConnection } = useUpdateConnection();
  const workspace = useCurrentWorkspace();
  const { hasFeature } = useFeatureService();

  const supportsNormalization = definition.supportsNormalization;
  const supportsDbt = hasFeature(FeatureItem.AllowCustomDBT) && definition.supportsDbt;

  const mode = connection.status === ConnectionStatus.DEPRECATED ? "readonly" : "edit";

  const onSubmit: FormikOnSubmit<{ transformations?: Transformation[]; normalization?: NormalizationType }> = async (
    values,
    { resetForm }
  ) => {
    const newOp = mapFormPropsToOperation(values, connection.operations, workspace.workspaceId);

    const operations = values.transformations
      ? connection.operations
          .filter((op) => op.operatorConfiguration.operatorType === OperatorType.Normalization)
          .concat(newOp)
      : newOp.concat(connection.operations.filter((op) => op.operatorConfiguration.operatorType === OperatorType.Dbt));

    await updateConnection({
      namespaceDefinition: connection.namespaceDefinition,
      namespaceFormat: connection.namespaceFormat,
      prefix: connection.prefix,
      schedule: connection.schedule,
      syncCatalog: connection.syncCatalog,
      connectionId: connection.connectionId,
      status: connection.status,
      operations: operations,
    });

    const nextFormValues: typeof values = {};
    if (values.transformations) {
      nextFormValues.transformations = getInitialTransformations(operations);
    }
    if (values.normalization) {
      nextFormValues.normalization = getInitialNormalization(operations, true);
    }

    resetForm({ values: nextFormValues });
  };

  return (
    <Content>
      <fieldset
        disabled={mode === "readonly"}
        style={{ border: "0", pointerEvents: `${mode === "readonly" ? "none" : "auto"}` }}
      >
        {supportsNormalization && (
          <NormalizationCard operations={connection.operations} onSubmit={onSubmit} mode={mode} />
        )}
        {supportsDbt && (
          <CustomTransformationsCard operations={connection.operations} onSubmit={onSubmit} mode={mode} />
        )}
        {!supportsNormalization && !supportsDbt && (
          <NoSupportedTransformationCard>
            <H4 center>
              <FormattedMessage id="connectionForm.operations.notSupported" />
            </H4>
          </NoSupportedTransformationCard>
        )}
      </fieldset>
    </Content>
  );
};

export default TransformationView;
