import React from "react";
import styled from "styled-components";

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
    </Label>
    {props.children}
  </ControlContainer>
);

export { ControlLabels };
