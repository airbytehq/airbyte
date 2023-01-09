import { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styled from "styled-components";

interface Props {
  className?: string;
  icon?: IconDefinition;
  variant?: "default" | "error";
}

const Box = styled.div<{ variant: "default" | "error" }>`
  background: ${({ theme, variant }) => (variant === "error" ? theme.red50 : theme.yellow100)};
  border-radius: 8px;
  padding: 18px 25px 22px;
  font-size: 14px;
  display: flex;
  gap: 8px;
  align-items: center;
`;

export const InfoBox: React.FC<React.PropsWithChildren<Props>> = ({
  children,
  className,
  icon,
  variant = "default",
}) => {
  return (
    <Box className={className} variant={variant}>
      {icon && <FontAwesomeIcon size="lg" icon={icon} />}
      {children}
    </Box>
  );
};
