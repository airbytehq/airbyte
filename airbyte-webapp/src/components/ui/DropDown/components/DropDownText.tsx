import styled from "styled-components";
import { Theme } from "theme";

interface DropDownTextProps {
  primary?: boolean;
  secondary?: boolean;
  fullText?: boolean;
}

const setColor = (props: DropDownTextProps & { theme: Theme }) => {
  if (props.primary) {
    return props.theme.primaryColor;
  }
  if (props.secondary) {
    return props.theme.greyColor40;
  }

  return "inherit";
};

export const DropDownText = styled.div<DropDownTextProps>`
  white-space: ${({ fullText }) => (fullText ? "normal" : "nowrap")};
  overflow: ${({ fullText }) => (fullText ? "inherit" : "hidden")};
  text-overflow: ${({ fullText }) => (fullText ? "inherit" : "ellipsis")};
  font-size: 14px;
  line-height: 20px;
  font-family: ${({ theme }) => theme.regularFont};
  font-style: normal;
  font-weight: normal;
  color: ${(props) => setColor(props)};

  .rw-list-option.rw-state-selected & {
    color: ${({ theme }) => theme.primaryColor};
  }
`;
