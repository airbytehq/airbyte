import { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styled from "styled-components";

interface Props {
  className?: string;
  icon?: IconDefinition;
}

const Box = styled.div`
  background: ${({ theme }) => theme.yellow100};
  border-radius: 8px;
  padding: 18px 25px 22px;
  font-size: 14px;
  display: flex;
  gap: 8px;
  align-items: center;
`;

export const InfoBox: React.FC<React.PropsWithChildren<Props>> = ({ children, className, icon }) => {
  return (
    <Box className={className}>
      {icon && <FontAwesomeIcon size="lg" icon={icon} />}
      <div>{children}</div>
    </Box>
  );
};
