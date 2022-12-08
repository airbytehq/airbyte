import { useMemo } from "react";

import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import { OctaviaRedFlagImage } from "./OctaviaRedFlagImage";
import { OctaviaYellowFlagImage } from "./OctaviaYellowFlagImage";
import styles from "./SchemaChangeOverlay.module.scss";
export const SchemaChangeOverlay: React.FC = () => {
  const {
    connection: { schemaChange },
  } = useConnectionFormService();

  const schemaChangeImage = useMemo(() => {
    if (schemaChange === "breaking") {
      return <OctaviaRedFlagImage />;
    } else if (schemaChange === "non_breaking") {
      return <OctaviaYellowFlagImage />;
    }
    return null;
  }, [schemaChange]);

  return (
    <div className={styles.background}>
      <div className={styles.schemaChangeImage}>{schemaChangeImage}</div>
    </div>
  );
};
