import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck } from "@fortawesome/free-solid-svg-icons";

const CheckBoxInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
  margin: 0;
  position: absolute;
`;

const CheckBoxContainer = styled.label<{ checked?: boolean }>`
  height: 18px;
  min-width: 18px;
  border: 1px solid
    ${({ theme, checked }) =>
      checked ? theme.primaryColor : theme.greyColor20};
  background: ${({ theme, checked }) =>
    checked ? theme.primaryColor : theme.whiteColor};
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

const CheckBox: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = (
  props
) => (
  <CheckBoxContainer
    onClick={(event: React.SyntheticEvent) => event.stopPropagation()}
    className={props.className}
    checked={props.checked}
  >
    <CheckBoxInput {...props} type="checkbox" />
    {props.checked && <FontAwesomeIcon icon={faCheck} />}
  </CheckBoxContainer>
);

export default CheckBox;
