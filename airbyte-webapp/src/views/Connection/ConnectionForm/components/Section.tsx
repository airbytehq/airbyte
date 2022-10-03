import { Card } from "components/ui";
import { Text } from "components/ui/Text";

import styles from "./Section.module.scss";

interface SectionProps {
  title?: React.ReactNode;
}

export const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({ title, children }) => (
  <Card>
    <div className={styles.section}>
      {title && (
        <Text as="h5" size="sm">
          {title}
        </Text>
      )}
      {children}
    </div>
  </Card>
);
