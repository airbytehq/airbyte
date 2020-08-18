import React from "react";
import { FormattedMessage } from "react-intl";

import Toggle from "../../../../../components/Toggle";
import Button from "../../../../../components/Button";
import styled from "styled-components";

type IProps = {
  enabled?: boolean;
  error?: boolean;
};

const SmallButton = styled(Button)`
  padding: 6px 8px 7px;
`;

const StatusCell: React.FC<IProps> = ({ enabled, error }) => {
  // TODO: add real actions
  const OnLaunch = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    console.log("Launch");
  };
  const OnToggleClick = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    console.log("ToggleClick");
  };

  if (!error) {
    return <Toggle checked={enabled} onClick={OnToggleClick} />;
  }

  return (
    <SmallButton onClick={OnLaunch}>
      <FormattedMessage id="sources.launch" />
    </SmallButton>
  );
};

export default StatusCell;
