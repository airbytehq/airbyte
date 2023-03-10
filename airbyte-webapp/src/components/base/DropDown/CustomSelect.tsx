import Select, { Props } from "react-select";
import styled from "styled-components";

export const CustomSelect = styled(Select)<
  {
    $withBorder?: boolean;
    $error?: boolean;
    $background?: string;
  } & Props
>`
  & > .react-select__control {
    height: ${({ $withBorder }) => ($withBorder ? 36 : 36)}px;

    box-shadow: none;
    border: 1px solid
      ${({ theme, $withBorder, $error }) =>
        $error ? theme.dangerColor : $withBorder ? theme.greyColor30 : theme.greyColor0};
    background: ${({ $background, theme }) => ($background ? $background : theme.greyColor0)};
    border-radius: 6px;
    font-size: 14px;
    //line-height: 20px;
    line-height: 16px;
    min-height: 36px;

    &:hover {
      border-color: ${({ theme, $error }) => ($error ? theme.dangerColor : theme.greyColor20)};
      background: ${({ $background, theme }) => ($background ? $background : theme.greyColor20)};
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
      display: flex;
      align-items: center;
      flex-wrap: nowrap;
    }
  }
`;
