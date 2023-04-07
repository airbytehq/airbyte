import { FieldProps } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { LabeledRadioButton } from "components";

import { NormalizationType } from "core/domain/connection/operation";

import { ConnectionFormMode } from "../ConnectionForm";

type NormalizationBlockProps = FieldProps<string> & {
  mode: ConnectionFormMode;
};

const NormalizationField: React.FC<NormalizationBlockProps> = ({ form, field, mode }) => {
  return (
    <div>
      <LabeledRadioButton
        {...form.getFieldProps(field.name)}
        id="normalization.raw"
        label={<FormattedMessage id="form.rawData" />}
        value={NormalizationType.raw}
        checked={field.value === NormalizationType.raw}
        disabled={mode === "readonly"}
      />
      <LabeledRadioButton
        {...form.getFieldProps(field.name)}
        id="normalization.basic"
        label={<FormattedMessage id="form.basicNormalization" />}
        value={NormalizationType.basic}
        checked={field.value === NormalizationType.basic}
        disabled={mode === "readonly"}
      />
    </div>
  );
};

export { NormalizationField };
