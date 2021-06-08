import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps } from "formik";

import { LabeledRadioButton, Link } from "components";
import { NormalizationType } from "core/domain/connector/operation";

const Normalization = styled.div`
  margin: 16px 0;
`;

type NormalizationBlockProps = {};

const NormalizationField: React.FC<NormalizationBlockProps> = () => {
  return (
    <Normalization>
      <Field name="normalization">
        {({ form, field }: FieldProps<string>) => (
          <>
            <LabeledRadioButton
              {...form.getFieldProps("normalization")}
              label={<FormattedMessage id="form.rawData" />}
              value={NormalizationType.RAW}
              checked={field.value === NormalizationType.RAW}
            />
            <LabeledRadioButton
              {...form.getFieldProps("normalization")}
              label={<FormattedMessage id="form.basicNormalization" />}
              value={NormalizationType.BASIC}
              checked={field.value === NormalizationType.BASIC}
              message={
                <FormattedMessage
                  id="form.basicNormalization.message"
                  values={{
                    lnk: (...lnk: React.ReactNode[]) => (
                      // TODO: add link href
                      <Link target="_blank" href={""} as="a">
                        {lnk}
                      </Link>
                    ),
                  }}
                />
              }
            />
          </>
        )}
      </Field>
    </Normalization>
  );
};

export default NormalizationField;
