import classNames from "classnames";
import { FormattedMessage } from "react-intl";

import { GAIcon } from "components/icons/GAIcon";
import { Tooltip } from "components/ui/Tooltip";

import { ReleaseStage } from "core/request/AirbyteClient";
import { useFeature, FeatureItem } from "hooks/services/Feature";
import { FreeTag } from "packages/cloud/components/experiments/FreeConnectorProgram";

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
  const fcpEnabled = useFeature(FeatureItem.FreeConnectorProgram);

  if (!stage) {
    return null;
  }

  const badge =
    stage === ReleaseStage.generally_available ? (
      <GAIcon />
    ) : (
      <div
        className={classNames(styles.pill, {
          [styles["pill--small"]]: small,
        })}
      >
        <FormattedMessage id={`connector.releaseStage.${stage}`} />
        {fcpEnabled && <FreeTag releaseStage={stage} />}
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
