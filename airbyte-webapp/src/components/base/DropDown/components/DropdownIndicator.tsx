import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { components, IndicatorProps, OptionTypeBase } from "react-select";
import styled from "styled-components";

const Arrow = styled(FontAwesomeIcon)`
  margin-top: -6px;
`;

const DropdownIndicator: React.FC<IndicatorProps<OptionTypeBase, false>> = (props) => (
  <components.DropdownIndicator {...props}>
    <Arrow icon={faSortDown} />
  </components.DropdownIndicator>
);

export default DropdownIndicator;
