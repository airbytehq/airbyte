import classNames from "classnames";

import { Card } from "components/ui/Card";
import { Heading } from "components/ui/Heading";

import styles from "./Section.module.scss";

interface SectionProps {
  title?: React.ReactNode;
  flush?: boolean;
  className?: string;
  flexHeight?: boolean;
}

export const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({
  title,
  flush,
  children,
  className,
  flexHeight,
}) => {
  return (
    <Card className={classNames({ [styles.flexHeight]: flexHeight })}>
      <div
        className={classNames(styles.section, { [styles.flush]: flush, [styles.flexHeight]: flexHeight }, className)}
      >
        {title && (
          <Heading as="h2" size="sm">
            {title}
          </Heading>
        )}
        {children}
      </div>
    </Card>
  );
};
