import styles from "./index.module.css";

interface MimeTypePillsProps {
  mimeType?: string;
}

export const MimeTypePills = ({ mimeType = "application/json" }: MimeTypePillsProps) => {
  return (
    <div className={styles.mimeTypePillsContainer}>
      <span className={styles.mimeTypePill}>{mimeType}</span>
    </div>
  );
};

export default MimeTypePills;
