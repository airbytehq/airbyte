import { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styled from "styled-components";

interface Props {
  className?: string;
  icon?: IconDefinition;
  error?: boolean;
}

const Box = styled.div<{ error?: boolean }>`
  background: ${({ theme, error }) => (error ? theme.red50 : theme.yellow100)};
  border-radius: 8px;
  padding: 18px 25px 22px;
  font-size: 14px;
  display: flex;
  gap: 8px;
  align-items: center;
`;

export const InfoBox: React.FC<React.PropsWithChildren<Props>> = ({ children, className, icon, error }) => {
  return (
    <Box className={className} error={error}>
      {icon && <FontAwesomeIcon size="lg" icon={icon} />}
      {children}
    </Box>
  );
};
