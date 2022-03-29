import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { FieldProps } from "formik";

import { useConfig } from "config";

import { LabeledRadioButton, Link } from "components";
import { NormalizationType } from "core/domain/connection/operation";

const Normalization = styled.div`
  margin: 16px 0;
`;

type NormalizationBlockProps = FieldProps<string>;

const NormalizationField: React.FC<
  NormalizationBlockProps & { disabled?: boolean }
> = ({ form, field, disabled }) => {
  const config = useConfig();

  return (
    <Normalization>
      <LabeledRadioButton
        {...form.getFieldProps(field.name)}
        id="normalization.raw"
        label={<FormattedMessage id="form.rawData" />}
        value={NormalizationType.RAW}
        checked={field.value === NormalizationType.RAW}
        disabled={disabled}
      />
      <LabeledRadioButton
        {...form.getFieldProps(field.name)}
        id="normalization.basic"
        label={<FormattedMessage id="form.basicNormalization" />}
        value={NormalizationType.BASIC}
        checked={field.value === NormalizationType.BASIC}
        disabled={disabled}
        message={
          <FormattedMessage
            id="form.basicNormalization.message"
            values={{
              lnk: (lnk: React.ReactNode) => (
                <Link target="_blank" href={config.ui.normalizationLink} as="a">
                  {lnk}
                </Link>
              ),
            }}
          />
        }
      />
    </Normalization>
  );
};

export { NormalizationField };
