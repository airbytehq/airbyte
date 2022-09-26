import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Tooltip } from "components/base/Tooltip";
import { GAIcon } from "components/icons/GAIcon";

import { ReleaseStage } from "core/request/AirbyteClient";

const Stage = styled.div<{ $small: boolean }>`
  display: inline-block;
  padding: 2px 6px;
  background: ${({ theme }) => theme.greyColor20};
  border-radius: 25px;
  text-transform: uppercase;
  font-size: ${({ $small }) => ($small ? "8px" : "10px")};
  line-height: initial;
  color: ${({ theme }) => theme.textColor};
`;

interface ReleaseStageBadgeProps {
  small?: boolean;
  stage?: ReleaseStage;
  /**
   * Whether to show a detailed message via a tooltip. If not specified, will be {@code true}.
   */
  tooltip?: boolean;
}

export const ReleaseStageBadge: React.FC<ReleaseStageBadgeProps> = ({ stage, small, tooltip = true }) => {
  if (!stage || stage === ReleaseStage.custom) {
    return null;
  }

  const badge =
    stage === ReleaseStage.generally_available ? (
      <GAIcon />
    ) : (
      <Stage $small={!!small}>
        <FormattedMessage id={`connector.releaseStage.${stage}`} />
      </Stage>
    );

  return tooltip ? (
    <Tooltip control={badge}>
      <FormattedMessage id={`connector.releaseStage.${stage}.description`} />
    </Tooltip>
  ) : (
    badge
  );
};
