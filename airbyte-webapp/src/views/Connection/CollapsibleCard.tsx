import React from "react";
import { useToggle } from "react-use";
import { Button, ContentCard } from "../../components";
import styled from "styled-components";

const Card = styled(ContentCard)`
  margin-bottom: 10px;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
`;

export type CollapsibleCardProps = {
  title: React.ReactNode;
  children: React.ReactNode;
  collapsible?: boolean;
  defaultCollapsedState?: boolean;
};

export const CollapsibleCard: React.FC<CollapsibleCardProps> = ({
  title,
  children,
  collapsible = false,
  defaultCollapsedState = false,
}) => {
  const [isCollapsed, toggle] = useToggle(defaultCollapsedState);

  return (
    <Card
      title={
        <CardHeader>
          {title}
          {collapsible && (
            <Button onClick={toggle}>replace me with arrow </Button>
          )}
        </CardHeader>
      }
    >
      {collapsible && isCollapsed ? true : children}
    </Card>
  );
};
