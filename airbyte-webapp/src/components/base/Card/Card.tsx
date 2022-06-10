import { classy } from "utils/components";

import styles from "./Card.module.scss";

interface CardProps {
  full?: boolean;
}

export const Card = classy("div", ({ full }: CardProps) => [
  styles.card,
  {
    [styles.full]: full,
  },
]);
