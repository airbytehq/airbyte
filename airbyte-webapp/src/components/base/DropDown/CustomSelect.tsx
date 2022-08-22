import Select, { Props } from "react-select";
import styled from "styled-components";

export const CustomSelect = styled(Select)<
  {
    $withBorder?: boolean;
    $error?: boolean;
  } & Props
>`
  & > .react-select__control {
    height: ${({ $withBorder }) => ($withBorder ? 31 : 36)}px;

    box-shadow: none;
    border: 1px solid
      ${({ theme, $withBorder, $error }) =>
        $error ? theme.dangerColor : $withBorder ? theme.greyColor30 : theme.greyColor0};
    background: ${({ theme }) => theme.greyColor0};
    border-radius: 4px;
    font-size: 14px;
    line-height: 20px;
    min-height: 36px;

    &:hover {
      border-color: ${({ theme, $error }) => ($error ? theme.dangerColor : theme.greyColor20)};
      background: ${({ theme }) => theme.greyColor20};
    }

    &.react-select__control--menu-is-open {
      border: 1px solid ${({ theme }) => theme.primaryColor};
      box-shadow: none;
      background: ${({ theme }) => theme.primaryColor12};
    }

    & .react-select__multi-value {
      background: rgba(255, 255, 255, 0);
    }

    & .react-select__value-container {
      overflow: visible;
    }
  }
`;
