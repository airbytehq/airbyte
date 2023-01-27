import { useIntl } from "react-intl";

import { ReleaseStage } from "core/request/AirbyteClient";

import styles from "./FreeTag.module.scss";
import { useFreeConnectorProgram } from "./hooks/useFreeConnectorProgram";

interface FreeTagProps {
  releaseStage: ReleaseStage;
}

// A tag labeling a release stage pill as free. Defined here for easy reuse between the
// two release stage pill implementations (which should likely be refactored!)
export const FreeTag: React.FC<FreeTagProps> = ({ releaseStage }) => {
  const { enrollmentStatusQuery } = useFreeConnectorProgram();
  const { isEnrolled } = enrollmentStatusQuery.data || {};
  const { formatMessage } = useIntl();

  return isEnrolled && ["alpha", "beta"].includes(releaseStage) ? (
    <span className={styles.freeTag}>{formatMessage({ id: "freeConnectorProgram.releaseStageBadge.free" })}</span>
  ) : null;
};
