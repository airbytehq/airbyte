import { Field, FieldProps, useFormikContext } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { DropDown } from "components/ui/DropDown";

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
        {({ field, form }: FieldProps<string>) => (
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
              <DropDown
                isDisabled={form.isSubmitting}
                options={geographies.map((geography) => ({
                  label: formatMessage({
                    id: `connection.geography.${geography}`,
                    defaultMessage: geography.toUpperCase(),
                  }),
                  value: geography,
                }))}
                value={field.value}
                onChange={(geography) => setFieldValue(name, geography.value)}
              />
            </div>
          </div>
        )}
      </Field>
    </Section>
  );
};
