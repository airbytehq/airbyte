import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { useSchemaChanges } from "hooks/connection/useSchemaChanges";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";

import { OctaviaRedFlagImage } from "./OctaviaRedFlagImage";
import { OctaviaYellowFlagImage } from "./OctaviaYellowFlagImage";
import styles from "./SchemaChangeOverlay.module.scss";
export const SchemaChangeOverlay: React.FC = () => {
  const {
    connection: { schemaChange },
    schemaHasBeenRefreshed,
  } = useConnectionEditService();

  const { hasBreakingSchemaChange, hasNonBreakingSchemaChange } = useSchemaChanges(schemaChange);

  const schemaChangeImage = useMemo(() => {
    if (hasBreakingSchemaChange) {
      return <OctaviaRedFlagImage />;
    } else if (hasNonBreakingSchemaChange) {
      return <OctaviaYellowFlagImage />;
    }
    return null;
  }, [hasBreakingSchemaChange, hasNonBreakingSchemaChange]);

  const schemaChangeMessage = useMemo(() => {
    if (schemaChange === "breaking") {
      return <FormattedMessage id="connectionForm.breakingChanges.message" />;
    }
    return null;
  }, [schemaChange]);

  if (!schemaChangeImage || !schemaChangeMessage || schemaHasBeenRefreshed) {
    return null;
  }
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div>{schemaChangeImage}</div>
        <Text className={styles.text}>{schemaChangeMessage}</Text>
      </div>
    </div>
  );
};
