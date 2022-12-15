import { FieldProps } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { LabeledRadioButton, Link } from "components";

import { NormalizationType } from "core/domain/connection/operation";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { links } from "utils/links";

import styles from "./NormalizationField.module.scss";

type NormalizationBlockProps = FieldProps<string>;

export const NormalizationField: React.FC<NormalizationBlockProps> = ({ form, field }) => {
  const { mode } = useConnectionFormService();

  return (
    <div className={styles.normalizationField}>
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
        message={
          mode !== "readonly" && (
            <FormattedMessage
              id="form.basicNormalization.message"
              values={{
                lnk: (lnk: React.ReactNode) => (
                  <Link target="_blank" href={links.normalizationLink} as="a">
                    {lnk}
                  </Link>
                ),
              }}
            />
          )
        }
      />
    </div>
  );
};
