import { components, MenuProps } from "react-select";
import styled from "styled-components";

import { DropDownOptionDataItem } from "./Option";

export const Menu = styled(components.Menu)<MenuProps<DropDownOptionDataItem, false>>`
  background: ${({ theme }) => theme.textColor};

  &.react-select__menu {
    margin: 0;
    min-width: 260px;
    border-radius: 4px;
    background: ${({ theme }) => theme.whiteColor};
    box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04), 0 3px 14px 0 rgba(11, 10, 26, 0.08),
      0 5px 5px 0 rgba(11, 10, 26, 0.12);

    & .react-select__option {
      padding: 0;
      margin: 0;
      background: ${({ theme }) => theme.whiteColor};

      &.react-select__option--is-selected,
      &.react-select__option--is-focused {
        background: rgba(255, 255, 255, 0);
      }
    }
  }
`;
