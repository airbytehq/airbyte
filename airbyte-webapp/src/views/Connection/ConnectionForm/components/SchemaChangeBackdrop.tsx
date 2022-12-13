import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { useSchemaChanges } from "hooks/connection/useSchemaChanges";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import { OctaviaRedFlag } from "./OctaviaRedFlag";
import { OctaviaYellowFlag } from "./OctaviaYellowFlag";
import styles from "./SchemaChangeBackdrop.module.scss";

export const SchemaChangeBackdrop: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const allowAutoDetectSchemaChanges = useFeature(FeatureItem.AllowAutoDetectSchemaChanges);

  const {
    schemaHasBeenRefreshed,
    connection: { schemaChange },
  } = useConnectionEditService();

  const { hasBreakingSchemaChange, hasNonBreakingSchemaChange } = useSchemaChanges(schemaChange);

  const schemaChangeMessage = useMemo(() => {
    return hasBreakingSchemaChange ? (
      <FormattedMessage id="connectionForm.breakingChanges.backdrop.message" />
    ) : hasNonBreakingSchemaChange ? (
      <FormattedMessage id="connectionForm.nonBreakingChanges.backdrop.message" />
    ) : null;
  }, [hasBreakingSchemaChange, hasNonBreakingSchemaChange]);

  const schemaChangeImage = useMemo(() => {
    return hasBreakingSchemaChange ? <OctaviaRedFlag /> : hasNonBreakingSchemaChange ? <OctaviaYellowFlag /> : null;
  }, [hasBreakingSchemaChange, hasNonBreakingSchemaChange]);

  if (
    !allowAutoDetectSchemaChanges ||
    (!hasBreakingSchemaChange && !hasNonBreakingSchemaChange) ||
    schemaHasBeenRefreshed
  ) {
    return <>{children}</>;
  }

  return (
    <div className={styles.schemaChangeBackdropContainer}>
      <div className={styles.backdrop}>
        <div className={styles.contentContainer}>
          <div>{schemaChangeImage}</div>
          <Text className={styles.text}>{schemaChangeMessage}</Text>
        </div>
      </div>
      {children}
    </div>
  );
};
