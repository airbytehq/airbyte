import classNames from "classnames";
import { FormattedMessage, useIntl } from "react-intl";

import { GAIcon } from "components/icons/GAIcon";
import { Tooltip } from "components/ui/Tooltip";

import { ReleaseStage } from "core/request/AirbyteClient";
import { useFreeConnectorProgramInfo } from "packages/cloud/components/experiments/FreeConnectorProgram/hooks/useFreeConnectorProgram";

import styles from "./ReleaseStageBadge.module.scss";

interface ReleaseStageBadgeProps {
  small?: boolean;
  stage?: ReleaseStage;
  /**
   * Whether to show a detailed message via a tooltip. If not specified, will be {@code true}.
   */
  tooltip?: boolean;
}

export const ReleaseStageBadge: React.FC<ReleaseStageBadgeProps> = ({ stage, small, tooltip = true }) => {
  const { data } = useFreeConnectorProgramInfo();
  const showEnrollmentUi = Boolean(data?.showEnrollmentUi) || true;
  const { formatMessage } = useIntl();

  const showFreeTag = showEnrollmentUi && (stage === "alpha" || stage === "beta");

  if (!stage || stage === ReleaseStage.custom) {
    return null;
  }

  const badge =
    stage === ReleaseStage.generally_available ? (
      <GAIcon />
    ) : (
      <div
        className={classNames(styles.pill, {
          [styles["pill--small"]]: small,
          [styles["pill--contains-tag"]]: showFreeTag,
        })}
      >
        <FormattedMessage id={`connector.releaseStage.${stage}`} />
        {showFreeTag && (
          <span className={styles.freeTag}>{formatMessage({ id: "freeConnectorProgram.releaseStageBadge.free" })}</span>
        )}
      </div>
    );

  return tooltip ? (
    <Tooltip control={badge}>
      <FormattedMessage id={`connector.releaseStage.${stage}.description`} />
    </Tooltip>
  ) : (
    badge
  );
};
