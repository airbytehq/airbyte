import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import { Card } from "components/ui/Card";

import styles from "./ConnectionBlock.module.scss";
import { ConnectionBlockItem, Content } from "./ConnectionBlockItem";

interface IProps {
  itemFrom?: { name: string; icon?: string };
  itemTo?: { name: string; icon?: string };
}

export const ConnectionBlock: React.FC<IProps> = (props) => (
  <Card className={classNames(styles.lightContentCard)}>
    {props.itemFrom ? <ConnectionBlockItem {...props.itemFrom} /> : <Content className={styles.extraBlock} />}
    <FontAwesomeIcon className={styles.arrow} icon={faChevronRight} />
    {props.itemTo ? <ConnectionBlockItem {...props.itemTo} /> : <Content className={styles.extraBlock} />}
  </Card>
);
