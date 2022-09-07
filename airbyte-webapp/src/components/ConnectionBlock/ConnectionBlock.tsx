import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import classNames from "classnames";
import styled from "styled-components";
import styles from "./ConnectionBlock.module.scss";

import { Card } from "../base/Card";
import { ConnectionBlockItem, Content } from "./components/ConnectionBlockItem";

interface IProps {
  className?: string;
  itemFrom?: { name: string; icon?: string };
  itemTo?: { name: string; icon?: string };
}

// const LightContentCard = styled(Card)`
//   display: flex;
//   justify-content: space-between;
//   align-items: center;
//   flex-direction: row;
//   padding: 20px 21px 19px;
//   margin-bottom: 12px;
// `;

// const LightContentCard = ({ children }) => {
//   return (
//     <Card className={styles.lightContentCard}>
//       {children }
//     </Card>
//   )
// }

const Arrow = styled(FontAwesomeIcon)`
  font-size: 29px;
  line-height: 29px;
  color: ${({ theme }) => theme.primaryColor};
`;

const ExtraBlock = styled(Content)`
  background: none;
`;

const ConnectionBlock: React.FC<IProps> = (props) => (
  <Card className={classNames(styles.lightContentCard)}>
    {props.itemFrom ? <ConnectionBlockItem {...props.itemFrom} /> : <ExtraBlock />}
    <Arrow icon={faChevronRight} />
    {props.itemTo ? <ConnectionBlockItem {...props.itemTo} /> : <ExtraBlock />}
  </Card>
);

export default ConnectionBlock;
