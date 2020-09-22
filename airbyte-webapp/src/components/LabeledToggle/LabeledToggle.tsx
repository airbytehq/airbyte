import React from "react";
import styled from "styled-components";
import { FormattedHTMLMessage } from "react-intl";
import Toggle from "../Toggle";

type IProps = {
  message?: React.ReactNode;
  label?: React.ReactNode;
} & React.InputHTMLAttributes<HTMLInputElement>;

const ToggleContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Label = styled.label<{ disabled?: boolean }>`
  padding-left: 7px;
  font-size: 13px;
  line-height: 16px;
  color: ${({ theme, disabled }) =>
    disabled ? theme.greyColor40 : theme.textColor};
  cursor: ${({ disabled }) => (disabled ? "auto" : "pointer")};
`;

const AdditionMessage = styled.span`
  padding-left: 5px;
  color: ${({ theme }) => theme.greyColor40};
`;

const LabeledToggle: React.FC<IProps> = props => {
  console.log("hello");
  console.log(props);
  console.log(props.message);
  return (
    <ToggleContainer>
      <Toggle {...props} id={`toggle-${props.name}`} />
      <Label disabled={props.disabled} htmlFor={`toggle-${props.name}`}>
        {props.label}
        <AdditionMessage>
          <FormattedHTMLMessage
            id="1"
            defaultMessage={(props.message as string) || ""}
          />
        </AdditionMessage>
      </Label>
    </ToggleContainer>
  );
};

export default LabeledToggle;
