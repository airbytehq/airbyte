import styled from "styled-components";
import { IProps } from "./types";

type IStyleProps = IProps & { theme: any };

const getBorderColor = (props: IStyleProps) => {
  if ((props.secondary && props.wasActive) || props.iconOnly) {
    return "transparent";
  }

  if (props.secondary) {
    return props.theme.greyColor30;
  } else if (props.danger) {
    return props.theme.dangerColor;
  }

  return props.theme.primaryColor;
};

const getBackgroundColor = (props: IStyleProps) => {
  if (props.wasActive) {
    if (props.secondary || props.iconOnly) {
      return props.theme.primaryColor12;
    }
    return "transparent";
  } else if (props.secondary || props.iconOnly) {
    return "transparent";
  } else if (props.danger) {
    return props.theme.dangerColor;
  }

  return props.theme.primaryColor;
};

const getTextColor = (props: IStyleProps) => {
  if (props.wasActive) {
    if (props.danger) {
      return props.theme.dangerColor;
    }
    return props.theme.primaryColor;
  } else if (props.secondary || props.iconOnly) {
    return props.theme.greyColor60;
  }

  return props.theme.whiteColor;
};

const getDisabledTextColor = (props: IStyleProps) => {
  if (props.danger) {
    return props.theme.dangerColor;
  } else if (props.iconOnly) {
    return props.theme.greyColor40;
  }

  return getTextColor(props);
};

const getDisabledOpacity = (props: IStyleProps) => {
  if (props.danger) {
    return ".5";
  } else if (props.iconOnly) {
    return "1";
  }

  return ".3";
};

const getShadowOnHover = (props: IStyleProps) => {
  if (
    props.secondary ||
    props.iconOnly ||
    (props.wasActive && !props.clickable)
  ) {
    return "none";
  }

  return "0 1px 3px rgba(53, 53, 66, .2), 0 1px 2px rgba(53, 53, 66, .12), 0 1px 1px rgba(53, 53, 66, .14)";
};

const Button = styled.button<IProps>`
  width: ${props => (props.full ? "100%" : "auto")};
  display: ${props => (props.full ? "block" : "inline-block")};
  border: 1px solid ${props => getBorderColor(props)};
  outline: none;
  border-radius: 4px;
  padding: ${props => (props.iconOnly ? "1.5px 3px" : "5px 16px 6px")};
  font-weight: 500;
  font-size: ${props => (props.iconOnly ? 14 : 12)}px;
  line-height: 15px;
  text-align: center;
  letter-spacing: 0.03em;
  cursor: pointer;
  pointer-events: ${props =>
    props.wasActive && !props.clickable ? "none" : "all"};
  color: ${props => getTextColor(props)};
  background: ${props => getBackgroundColor(props)};
  text-decoration: none;

  &:disabled {
    opacity: ${props => getDisabledOpacity(props)};
    background: ${props => props.danger && "transparent"};
    border: ${props => props.danger && "none"};
    color: ${props => getDisabledTextColor(props)};
    pointer-events: none;
  }

  &:hover {
    box-shadow: ${props => getShadowOnHover(props)};
    border-color: ${props =>
      (props.secondary && props.theme.greyColor40) ||
      (props.iconOnly && props.theme.greyColor20)};
    color: ${props =>
      (props.secondary || props.iconOnly) && props.theme.textColor};
  }
`;

export default Button;
