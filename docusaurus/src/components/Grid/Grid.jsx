

import React from 'react';
import styles from './Grid.module.css';

export const Grid = ({ children, columns = "1" }) => {
  return (
    <div className={`${styles.grid} ${styles[`grid-columns-${columns}`]}`}>
      {children}
    </div>
  );
};

export default Grid;
