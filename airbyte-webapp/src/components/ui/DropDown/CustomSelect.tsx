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
        $error ? theme.red100 : $withBorder ? theme.greyColor30 : theme.greyColor0};
    background: ${({ theme }) => theme.greyColor0};
    border-radius: 4px;
    font-size: 14px;
    line-height: 20px;
    min-height: 36px;
    flex-wrap: nowrap;

    &:not(:focus-within, :disabled):hover {
      border-color: ${({ theme, $error }) => ($error ? theme.red : undefined)};
    }

    &:hover {
      border-color: ${({ theme }) => theme.greyColor10};
    }

    &.react-select__control--menu-is-open,
    &:focus-within {
      border: 1px solid ${({ theme }) => theme.primaryColor};
      box-shadow: none;
    }

    & .react-select__multi-value {
      background: rgba(255, 255, 255, 0);
    }

    & .react-select__value-container {
      overflow: hidden;
      display: flex;
      flex-wrap: nowrap;
    }
  }
`;
