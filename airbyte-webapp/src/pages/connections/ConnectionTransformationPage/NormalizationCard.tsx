import { Field } from "formik";
import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionEditFormCard } from "components/connection/ConnectionEditFormCard";
import { getInitialNormalization } from "components/connection/ConnectionForm/formConfig";
import { NormalizationField } from "components/connection/ConnectionForm/NormalizationField";

import { NormalizationType } from "core/domain/connection";
import { OperationRead } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FormikOnSubmit } from "types/formik";

export const NormalizationCard: React.FC<{
  operations?: OperationRead[];
  onSubmit: FormikOnSubmit<{ normalization?: NormalizationType }>;
}> = ({ operations, onSubmit }) => {
  const { mode } = useConnectionFormService();
  const initialValues = useMemo(
    () => ({
      normalization: getInitialNormalization(operations, true),
    }),
    [operations]
  );

  return (
    <ConnectionEditFormCard<{ normalization?: NormalizationType }>
      form={{
        initialValues,
        onSubmit,
      }}
      title={<FormattedMessage id="connection.normalization" />}
      collapsible
    >
      <Field name="normalization" component={NormalizationField} mode={mode} />
    </ConnectionEditFormCard>
  );
};
