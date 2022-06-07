import styled from "styled-components";
import { Theme } from "theme";

interface IProps {
  primary?: boolean;
  secondary?: boolean;
  fullText?: boolean;
}

const setColor = (props: IProps & { theme: Theme }) => {
  if (props.primary) {
    return props.theme.primaryColor;
  }
  if (props.secondary) {
    return props.theme.greyColor40;
  }

  return "inherit";
};

const Text = styled.div<IProps>`
  white-space: ${({ fullText }) => (fullText ? "normal" : "nowrap")};
  overflow: ${({ fullText }) => (fullText ? "inherit" : "hidden")};
  text-overflow: ${({ fullText }) => (fullText ? "inherit" : "ellipsis")};
  font-size: 14px;
  line-height: 20px;
  font-family: ${({ theme }) => theme.regularFont};
  font-style: normal;
  font-weight: normal;
  max-width: 94%;
  color: ${(props) => setColor(props)};

  .rw-list-option.rw-state-selected & {
    color: ${({ theme }) => theme.primaryColor};
  }
`;

export default Text;
