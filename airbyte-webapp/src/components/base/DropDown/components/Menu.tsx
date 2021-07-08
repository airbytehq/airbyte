import React from "react";
import { components, MenuProps, OptionTypeBase } from "react-select";
import styled from "styled-components";
import { theme } from "theme";
import { IDataItem } from "./Option";

// function getLength(options) {
//   return options.reduce((acc, curr) => {
//     if (curr.options) return acc + getLength(curr.options);
//     return acc + 1;
//   }, 0);
// }

// const menuHeaderStyle = {
//   padding: "8px 12px",
// };

// const Menu = (props) => {
//   const optionsLength = getLength(props.options);
//   return (
//     <Fragment>
//       <div style={menuHeaderStyle}>
//         Custom Menu with {optionsLength} options
//       </div>
//       <components.Menu {...props}>{props.children}</components.Menu>
//     </Fragment>
//   );
// };

const MenuList = styled(components.Menu)`
  background: ${theme.textColor};
  background: red;

  &.react-select__menu {
    margin: 0;
    min-width: 260px;
    border-radius: 4px;
    background: ${({ theme }) => theme.whiteClor};
    box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04),
      0 3px 14px 0 rgba(11, 10, 26, 0.08), 0 5px 5px 0 rgba(11, 10, 26, 0.12);

    & .react-select__option {
      cursor: pointer;
      color: ${theme.textColor};
      border: none;
      padding: 10px 16px;
      font-size: 14px;
      line-height: 19px;

      &.react-select__option--is-focused {
        background: ${theme.greyColor20};
      }

      &.react-select__option--is-selected {
        background: ${theme.primaryColor12};
        color: ${theme.primaryColor};
      }
    }
  }
`;

const Menu: React.FC<MenuProps<IDataItem, boolean>> = (props) => {
  return <MenuList {...props}>{props.children}</MenuList>;
};

export default Menu;
