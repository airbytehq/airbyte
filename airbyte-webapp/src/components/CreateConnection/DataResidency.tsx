import { Field, FieldProps, useFormikContext } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import { DataGeographyDropdown } from "components/common/DataGeographyDropdown";
import { ControlLabels } from "components/LabeledControl";

import { Geography } from "core/request/AirbyteClient";
import { useAvailableGeographies } from "packages/cloud/services/geographies/GeographiesService";
import { links } from "utils/links";
import { Section } from "views/Connection/ConnectionForm/components/Section";

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
          <div className={styles.flexRow}>
            <div className={styles.leftFieldCol}>
              <ControlLabels
                nextLine
                label={<FormattedMessage id="connection.geographyTitle" />}
                message={
                  <FormattedMessage
                    id="connection.geographyDescription"
                    values={{
                      lnk: (node: React.ReactNode) => (
                        <a href={links.cloudAllowlistIPsLink} target="_blank" rel="noreferrer">
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
          </div>
        )}
      </Field>
    </Section>
  );
};
