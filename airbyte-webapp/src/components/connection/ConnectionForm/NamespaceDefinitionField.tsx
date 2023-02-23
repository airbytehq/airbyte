import { FieldProps, useField } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { DropDown } from "components/ui/DropDown";
import { FlexContainer } from "components/ui/Flex";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";

import styles from "./NamespaceDefinitionField.module.scss";

export const StreamOptions = [
  {
    value: NamespaceDefinitionType.destination,
    label: <FormattedMessage id="connectionForm.destinationFormat" />,
    testId: "namespaceDefinition-destination",
  },
  {
    value: NamespaceDefinitionType.source,
    label: <FormattedMessage id="connectionForm.sourceFormat" />,
    testId: "namespaceDefinition-source",
  },
  {
    value: NamespaceDefinitionType.customformat,
    label: <FormattedMessage id="connectionForm.customFormat" />,
    testId: "namespaceDefinition-customformat",
  },
];

export const NamespaceDefinitionField: React.FC<FieldProps<string>> = ({ field, form }) => {
  const [, meta] = useField(field.name);

  return (
    <FlexContainer alignItems="center">
      <div className={styles.leftFieldCol}>
        <ControlLabels
          nextLine
          error={!!meta.error && meta.touched}
          label={<FormattedMessage id="connectionForm.namespaceDefinition.title" />}
          infoTooltipContent={<FormattedMessage id="connectionForm.namespaceDefinition.subtitle" />}
        />
      </div>
      <div className={styles.rightFieldCol}>
        <DropDown
          name="namespaceDefinition"
          error={!!meta.error && meta.touched}
          options={StreamOptions}
          value={field.value}
          onChange={({ value }) => form.setFieldValue(field.name, value)}
        />
      </div>
    </FlexContainer>
  );
};
