import { faCheck, faMinus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

const CheckBoxInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
  margin: 0;
  position: absolute;
`;

const CheckBoxContainer = styled.label<{
  checked?: boolean;
  indeterminate?: boolean;
}>`
  height: 18px;
  min-width: 18px;
  border: 1px solid
    ${({ theme, checked, indeterminate }) => (checked || indeterminate ? theme.primaryColor : theme.greyColor20)};
  background: ${({ theme, checked, indeterminate }) =>
    checked || indeterminate ? theme.primaryColor : theme.whiteColor};
  color: ${({ theme }) => theme.whiteColor};
  text-align: center;
  border-radius: 4px;
  font-size: 13px;
  line-height: 13px;
  display: inline-block;
  padding: 1px 0;
  cursor: pointer;
  vertical-align: top;
  position: relative;
`;

export const CheckBox: React.FC<React.InputHTMLAttributes<HTMLInputElement> & { indeterminate?: boolean }> = ({
  indeterminate,
  ...props
}) => (
  <CheckBoxContainer
    onClick={(event: React.SyntheticEvent) => event.stopPropagation()}
    className={props.className}
    checked={props.checked}
    indeterminate={indeterminate}
  >
    <CheckBoxInput {...props} type="checkbox" />
    {indeterminate ? <FontAwesomeIcon icon={faMinus} /> : props.checked && <FontAwesomeIcon icon={faCheck} />}
  </CheckBoxContainer>
);
