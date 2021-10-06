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

const CheckBoxContainer = styled.label`
  height: 20px;
  min-width: 20px;
  background: ${({ theme }) => theme.greyColor20};
  color: ${({ theme }) => theme.primaryColor};
  text-align: center;
  border-radius: 4px;
  font-size: 14px;
  line-height: 14px;
  display: inline-block;
  padding: 2px 0;
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
  >
    <CheckBoxInput {...props} type="checkbox" />
    {props.checked && <FontAwesomeIcon icon={faCheck} />}
  </CheckBoxContainer>
);

export default CheckBox;
