import { NavLink, To } from "react-router-dom";

import { FlexContainer } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import { useCalculateSidebarStyles } from "../GenericSideBar";

interface CustomNavLinkProps {
  label: React.ReactNode;
  icon: React.ReactNode;
  to: To;
  testId: string;
}

export const CustomNavLink: React.FC<CustomNavLinkProps> = ({ label, icon, to, testId }) => {
  const navLinkClassName = useCalculateSidebarStyles();
  return (
    <NavLink className={navLinkClassName} to={to} data-testid={testId}>
      <FlexContainer direction="column" alignItems="center" justifyContent="space-between">
        {icon}
        <Text size="sm">{label}</Text>
      </FlexContainer>
    </NavLink>
  );
};
