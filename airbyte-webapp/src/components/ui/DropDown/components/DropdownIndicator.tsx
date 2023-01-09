import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { components, DropdownIndicatorProps } from "react-select";
import styled from "styled-components";

const Arrow = styled(FontAwesomeIcon)`
  margin-top: -6px;
`;

export const DropdownIndicator: React.FC<DropdownIndicatorProps> = (props) => (
  <components.DropdownIndicator {...props}>
    <Arrow icon={faSortDown} />
  </components.DropdownIndicator>
);
