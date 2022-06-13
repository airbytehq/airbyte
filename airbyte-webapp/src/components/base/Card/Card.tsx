import { classy } from "utils/components";

import styles from "./Card.module.scss";

interface CardProps {
  full?: boolean;
}

export const Card = classy<CardProps>("div", ({ full }) => [
  styles.card,
  {
    [styles.full]: full,
  },
]);
