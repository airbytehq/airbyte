import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { useIsAutoDetectSchemaChangesEnabled } from "hooks/connection/useIsAutoDetectSchemaChangesEnabled";

import { OctaviaRedFlagImage } from "./OctaviaRedFlagImage";
import styles from "./SchemaChangeBackdrop.module.scss";

interface SchemaChangeBackdropProps {
  hasBreakingSchemaChange: boolean;
  schemaHasBeenRefreshed: boolean;
}
export const SchemaChangeBackdrop: React.FC<React.PropsWithChildren<SchemaChangeBackdropProps>> = ({
  hasBreakingSchemaChange,
  schemaHasBeenRefreshed,
  children,
}) => {
  const isAutoDetectSchemaChangesEnabled = useIsAutoDetectSchemaChangesEnabled();

  if (schemaHasBeenRefreshed || !hasBreakingSchemaChange || !isAutoDetectSchemaChangesEnabled) {
    return <>{children}</>;
  }
  const schemaChangeImage = <OctaviaRedFlagImage />;

  const schemaChangeMessage = <FormattedMessage id="connectionForm.breakingChanges.message" />;

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
