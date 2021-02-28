import React from "react";
import styled from "styled-components";

import Label from "components/Label";

export type ControlLabelsProps = {
  className?: string;
  error?: boolean;
  success?: boolean;
  message?: React.ReactNode;
  labelAdditionLength?: number;
  label?: React.ReactNode;
};

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
    >
      {props.label}
    </Label>
    {props.children}
  </ControlContainer>
);

export { ControlLabels };
