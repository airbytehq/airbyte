import { useFormikContext } from "formik";
import { FormattedMessage } from "react-intl";

import { FlexContainer } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import {
  ConnectionScheduleData,
  ConnectionScheduleType,
  NamespaceDefinitionType,
  NonBreakingChangesPreference,
} from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import styles from "./ConnectionConfigurationFormPreview.module.scss";
import { FormikConnectionFormValues } from "./formConfig";
import { namespaceDefinitionOptions } from "./types";
import { StreamNameDefinitionValueType } from "../DestinationStreamNamesModal/DestinationStreamNamesModal";

export const ConnectionConfigurationFormPreview: React.FC = () => {
  const { getFieldMeta } = useFormikContext<FormikConnectionFormValues>();
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

  const scheduleType = getFieldMeta<ConnectionScheduleType>("scheduleType").value;
  const scheduleData = getFieldMeta<ConnectionScheduleData>("scheduleData").value;
  const nonBreakingChangesPreference = getFieldMeta<NonBreakingChangesPreference>("nonBreakingChangesPreference").value;
  const destNamespaceDef = getFieldMeta("namespaceDefinition").value as NamespaceDefinitionType;
  const destNamespaceFormat = getFieldMeta("namespaceFormat").value;
  const destPrefix = getFieldMeta("prefix").value;

  const frequency = (
    <div>
      <Text size="xs" color="grey">
        <FormattedMessage id="form.frequency" />:
      </Text>
      <Text size="md" color="grey">
        {scheduleType === ConnectionScheduleType.manual && <FormattedMessage id="frequency.manual" />}
        {scheduleType === ConnectionScheduleType.cron && (
          <>
            <FormattedMessage id="frequency.cron" /> - {scheduleData?.cron?.cronExpression}{" "}
            {scheduleData?.cron?.cronTimeZone}
          </>
        )}
        {scheduleType === ConnectionScheduleType.basic && (
          <FormattedMessage
            id={`form.every.${scheduleData?.basicSchedule?.timeUnit}`}
            values={{ value: scheduleData?.basicSchedule?.units }}
          />
        )}
      </Text>
    </div>
  );

  const destinationNamespace = (
    <div>
      <Text size="xs" color="grey">
        <FormattedMessage id="connectionForm.namespaceDefinition.title" />:
      </Text>
      <Text size="md" color="grey">
        <FormattedMessage id={`connectionForm.${namespaceDefinitionOptions[destNamespaceDef]}`} />
        {namespaceDefinitionOptions[destNamespaceDef] === namespaceDefinitionOptions.customformat && (
          <>
            {" - "}
            {destNamespaceFormat}
          </>
        )}
      </Text>
    </div>
  );

  const destinationPrefix = (
    <div>
      <Text size="xs" color="grey">
        <FormattedMessage id="form.prefix" />:
      </Text>
      <Text size="md" color="grey">
        {destPrefix === StreamNameDefinitionValueType.Prefix || destPrefix === "" ? ( // is prefix is reserved word? we cant use it as a value
          <FormattedMessage id="connectionForm.modal.destinationStreamNames.radioButton.mirror" />
        ) : (
          destPrefix
        )}
      </Text>
    </div>
  );

  const nonBreakingChanges = allowAutoDetectSchema && (
    <div>
      <Text size="xs" color="grey">
        <FormattedMessage id="connectionForm.nonBreakingChangesPreference.label" />:
      </Text>
      <Text size="md" color="grey">
        <FormattedMessage id={`connectionForm.nonBreakingChangesPreference.${nonBreakingChangesPreference}`} />
      </Text>
    </div>
  );

  return (
    <FlexContainer className={styles.container}>
      {frequency}
      {destinationNamespace}
      {destinationPrefix}
      {nonBreakingChanges}
    </FlexContainer>
  );
};
