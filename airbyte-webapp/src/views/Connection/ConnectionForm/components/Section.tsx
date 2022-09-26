import { Card } from "components/base";
import { Text } from "components/base/Text";

import styles from "./Section.module.scss";

interface SectionProps {
  title?: React.ReactNode;
}

export const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({ title, children }) => (
  <Card>
    <div className={styles.section}>
      {title && <Text as="h5">{title}</Text>}
      {children}
    </div>
  </Card>
);
