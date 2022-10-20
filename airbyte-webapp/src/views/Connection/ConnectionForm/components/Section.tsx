import { Card } from "components/ui/Card";
import { Text } from "components/ui/Text";

import styles from "./Section.module.scss";

interface SectionProps {
  title?: React.ReactNode;
}

export const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({ title, children }) => (
  <Card>
    <div className={styles.section}>
      {title && (
        <Text as="h2" size="sm">
          {title}
        </Text>
      )}
      {children}
    </div>
  </Card>
);
