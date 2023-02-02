import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { useSchemaChanges } from "hooks/connection/useSchemaChanges";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import { OctaviaRedFlag } from "./OctaviaRedFlag";
import { OctaviaYellowFlag } from "./OctaviaYellowFlag";
import styles from "./SchemaChangeBackdrop.module.scss";

export const SchemaChangeBackdrop: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

  const {
    schemaHasBeenRefreshed,
    connection: { schemaChange },
  } = useConnectionEditService();

  const { hasBreakingSchemaChange, hasNonBreakingSchemaChange } = useSchemaChanges(schemaChange);

  if (!allowAutoDetectSchema || !hasBreakingSchemaChange || schemaHasBeenRefreshed) {
    return <>{children}</>;
  }

  return (
    <div className={styles.schemaChangeBackdropContainer} data-testid="schemaChangesBackdrop">
      <div className={styles.backdrop}>
        <div className={styles.contentContainer}>
          <div>
            {hasBreakingSchemaChange ? <OctaviaRedFlag /> : hasNonBreakingSchemaChange ? <OctaviaYellowFlag /> : null}
          </div>
          <Text className={styles.text}>
            <FormattedMessage id="connectionForm.schemaChangesBackdrop.message" />
          </Text>
        </div>
      </div>
      {children}
    </div>
  );
};
