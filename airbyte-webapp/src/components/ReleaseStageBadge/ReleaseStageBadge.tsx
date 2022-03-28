import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ReleaseStage } from "core/domain/connector";
import ToolTip from "components/ToolTip";

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

interface Props {
  small?: boolean;
  stage?: ReleaseStage;
  /**
   * Whether to show a detailed message via a tooltip. If not specified, will be {@code true}.
   */
  tooltip?: boolean;
}

export const ReleaseStageBadge: React.FC<Props> = ({
  stage,
  small,
  tooltip = true,
}) => {
  if (
    !stage ||
    stage === ReleaseStage.GENERALLY_AVAILABLE ||
    stage === ReleaseStage.CUSTOM
  ) {
    return null;
  }

  const badge = (
    <Stage $small={!!small}>
      <FormattedMessage id={`component.releaseStageBadge.${stage}.title`} />
    </Stage>
  );

  return tooltip ? (
    <ToolTip control={badge} cursor="help">
      <FormattedMessage id={`component.releaseStageBadge.${stage}.tooltip`} />
    </ToolTip>
  ) : (
    badge
  );
};
