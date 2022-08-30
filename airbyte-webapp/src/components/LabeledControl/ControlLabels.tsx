import React from "react";
import styled from "styled-components";

import { InfoTooltip } from "components/base/Tooltip";
import Label from "components/Label";

export interface ControlLabelsProps {
  className?: string;
  error?: boolean;
  success?: boolean;
  nextLine?: boolean;
  message?: React.ReactNode;
  errorMessage?: React.ReactNode;
  labelAdditionLength?: number;
  label?: React.ReactNode;
  infoMessage?: React.ReactNode;
}

const ControlContainer = styled.div`
  width: 100%;
  display: inline-block;
`;

const ControlLabels: React.FC<ControlLabelsProps> = (props) => (
  <ControlContainer className={props.className}>
    <Label
      error={props.error}
      success={props.success}
      message={props.message}
      additionLength={props.labelAdditionLength}
      nextLine={props.nextLine}
    >
      {props.label}
      {props.infoMessage && <InfoTooltip placement="top-start">{props.infoMessage}</InfoTooltip>}
    </Label>
    {props.children}
  </ControlContainer>
);

export { ControlLabels };
