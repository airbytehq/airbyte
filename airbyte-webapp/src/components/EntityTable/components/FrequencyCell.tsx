import React, { useMemo } from "react";
import styled from "styled-components";

import FrequencyConfig from "config/FrequencyConfig.json";
import { ConnectionSchedule } from "core/request/AirbyteClient";
import { equal } from "utils/objects";

interface FrequencyCellProps {
  value: ConnectionSchedule;
  enabled?: boolean;
}

const Content = styled.div<{ enabled?: boolean }>`
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inherit")};
`;

const FrequencyCell: React.FC<FrequencyCellProps> = ({ value, enabled }) => {
  const text = useMemo<string>(() => {
    const cellText = FrequencyConfig.find((item) => equal(item.config, value ?? null));
    return cellText?.text ?? "";
  }, [value]);

  return <Content enabled={enabled}>{text}</Content>;
};

export default FrequencyCell;
