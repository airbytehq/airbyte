import { Field, FieldProps, useFormikContext } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { DataGeographyDropdown } from "components/common/DataGeographyDropdown";
import { Section } from "components/connection/ConnectionForm/Section";
import { ControlLabels } from "components/LabeledControl";
import { FlexContainer } from "components/ui/Flex";

import { Geography } from "core/request/AirbyteClient";
import { useAvailableGeographies } from "packages/cloud/services/geographies/GeographiesService";
import { links } from "utils/links";

import styles from "./DataResidency.module.scss";

interface DataResidencyProps {
  name?: string;
}

export const DataResidency: React.FC<DataResidencyProps> = ({ name = "geography" }) => {
  const { formatMessage } = useIntl();
  const { setFieldValue } = useFormikContext();
  const { geographies } = useAvailableGeographies();

  return (
    <Section title={formatMessage({ id: "connection.geographyTitle" })}>
      <Field name={name}>
        {({ field, form }: FieldProps<Geography>) => (
          <FlexContainer alignItems="center">
            <div className={styles.leftFieldCol}>
              <ControlLabels
                nextLine
                optional
                label={<FormattedMessage id="connection.geographyTitle" />}
                infoTooltipContent={
                  <FormattedMessage
                    id="connection.geographyDescription"
                    values={{
                      ipLink: (node: React.ReactNode) => (
                        <a href={links.cloudAllowlistIPsLink} target="_blank" rel="noreferrer">
                          {node}
                        </a>
                      ),
                      docLink: (node: React.ReactNode) => (
                        <a href={links.connectionDataResidency} target="_blank" rel="noreferrer">
                          {node}
                        </a>
                      ),
                    }}
                  />
                }
              />
            </div>
            <div className={styles.rightFieldCol}>
              <DataGeographyDropdown
                isDisabled={form.isSubmitting}
                geographies={geographies}
                value={field.value}
                onChange={(geography) => setFieldValue(name, geography)}
              />
            </div>
          </FlexContainer>
        )}
      </Field>
    </Section>
  );
};
