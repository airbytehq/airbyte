import React from "react";
import styled from "styled-components";

import FrequencyConfig from "config/FrequencyConfig.json";
import { ScheduleProperties } from "core/domain/connection";
import { equal } from "utils/objects";

type IProps = {
  value: ScheduleProperties;
  enabled?: boolean;
};

const Content = styled.div<{ enabled?: boolean }>`
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inherit")};
`;

const FrequencyCell: React.FC<IProps> = ({ value, enabled }) => {
  const cellText = FrequencyConfig.find((item) => equal(item.config, value));
  return <Content enabled={enabled}>{cellText?.text || ""}</Content>;
};

export default FrequencyCell;
