import styled from "styled-components";

type IProps = {
  primary?: boolean;
  secondary?: boolean;
};

const setColor = (props: IProps & { theme: any }) => {
  if (props.primary) {
    return props.theme.primaryColor;
  }
  if (props.secondary) {
    return props.theme.greyColor40;
  }

  return "inhered";
};

const Text = styled.div<IProps>`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  line-height: 20px;
  font-family: ${({ theme }) => theme.regularFont};
  font-style: normal;
  font-weight: normal;
  max-width: 94%;
  color: ${props => setColor(props)};

  .rw-list-option.rw-state-selected & {
    color: ${({ theme }) => theme.primaryColor};
  }
`;

export default Text;
