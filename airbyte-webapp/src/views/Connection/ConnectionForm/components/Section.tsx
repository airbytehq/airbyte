import { Card } from "components/ui/Card";
import { Heading } from "components/ui/Heading";

import styles from "./Section.module.scss";

interface SectionProps {
  title?: React.ReactNode;
}

export const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({ title, children }) => (
  <Card>
    <div className={styles.section}>
      {title && (
        <Heading as="h2" size="sm">
          {title}
        </Heading>
      )}
      {children}
    </div>
  </Card>
);
