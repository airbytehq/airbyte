import { Multiselect as ReactMultiselect } from "react-widgets";
import { MultiselectProps as WidgetMultiselectProps } from "react-widgets/lib/Multiselect";
import styled from "styled-components";
import "react-widgets/dist/css/react-widgets.css";

export interface MultiselectProps extends WidgetMultiselectProps {
  disabled?: boolean;
  error?: boolean;
  name?: string;
}

export const Multiselect = styled(ReactMultiselect)<MultiselectProps>`
  box-shadow: none;
  padding: 0;
  margin: 0;

  & .rw-list-option.rw-state-focus,
  & .rw-list-option {
    color: ${({ theme }) => theme.textColor};
    border: none;
    padding: 10px 16px;
    font-size: 14px;
    line-height: 19px;
  }

  & .rw-list-option:hover {
    background: ${({ theme }) => theme.primaryColor12};
    color: ${({ theme }) => theme.primaryColor};
  }

  & .rw-list-option.rw-state-selected {
    background: ${({ theme }) => theme.primaryColor12};
    color: ${({ theme }) => theme.primaryColor};
    pointer-events: none;
  }

  & .rw-popup {
    border: 0.5px solid ${({ theme }) => theme.greyColor20};
    border-radius: 4px;
    box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04), 0 3px 14px 0 rgba(11, 10, 26, 0.08),
      0 5px 5px 0 rgba(11, 10, 26, 0.12);
  }

  & .rw-popup-container {
    & .rw-select {
      display: none;
    }

    & .rw-list-optgroup {
      width: 100%;
      padding: 0;
      border: none;
    }
  }

  & .rw-widget-container {
    box-shadow: none;
    outline: none;
    width: 100%;
    min-height: 37px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 14px;
    line-height: 20px;
    font-weight: normal;
    border: 1px solid ${(props) => (props.error ? props.theme.dangerColor : props.theme.greyColor0)};
    background: ${(props) => (props.error ? props.theme.greyColor10 : props.theme.greyColor0)};
    caret-color: ${({ theme }) => theme.primaryColor};

    & > div {
      vertical-align: middle;
    }

    & .rw-btn-select {
      color: ${({ theme }) => theme.primaryColor};
    }

    & input {
      padding: 0;
      height: auto;
      line-height: 26px;
    }

    &::placeholder {
      color: ${({ theme }) => theme.greyColor40};
    }

    &:hover {
      box-shadow: none;
      background: ${({ theme }) => theme.greyColor20};
      border-color: ${(props) => (props.error ? props.theme.dangerColor : props.theme.greyColor20)};
    }

    & .rw-multiselect-taglist {
      vertical-align: top;

      & .rw-multiselect-tag {
        background: ${({ theme }) => theme.mediumPrimaryColor};
        border-color: ${({ theme }) => theme.mediumPrimaryColor};
        color: ${({ theme }) => theme.whiteColor};
        border-radius: 4px;
        font-weight: 500;
        font-size: 12px;
        line-height: 21px;
        height: 23px;
        margin: 0 3px 0 0;
        padding: 0 4px 0 6px;

        & .rw-multiselect-tag-btn {
          color: ${({ theme }) => theme.greyColor55};
          font-size: 20px;
          line-height: 23px;
        }
      }
    }
  }

  &.rw-state-focus {
    & .rw-widget-container {
      background: ${({ theme }) => theme.primaryColor12};
      border-color: ${({ theme }) => theme.primaryColor};
    }
  }

  &.rw-state-disabled {
    & .rw-widget-container {
      pointer-events: none;
      color: ${({ theme }) => theme.greyColor55};
    }
  }
`;
