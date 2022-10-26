import classNames from "classnames";
import ReactPaginate, { ReactPaginateProps } from "react-paginate";

import styles from "./Paginator.module.scss";

type PaginatorProps = {
  numPages: number;
  onPageChange: (selectedPageIndex: number) => void;
  // pageRangeDisplayed?: 2 | 4 | 6 | 8 | 10;
} & Partial<Omit<ReactPaginateProps, "pageCount" | "onPageChange">>;

export const Paginator: React.FC<PaginatorProps> = ({
  numPages,
  onPageChange,
  breakLabel = "...",
  nextLabel = ">",
  previousLabel = "<",
  pageRangeDisplayed = 2,
  marginPagesDisplayed = 2,
  containerClassName,
  pageClassName,
  breakClassName,
  activeClassName,
  previousClassName,
  nextClassName,
  ...remainingProps
}) => {
  return (
    <ReactPaginate
      pageCount={numPages}
      onPageChange={(event) => {
        onPageChange(event.selected);
      }}
      breakLabel={breakLabel}
      nextLabel={nextLabel}
      previousLabel={previousLabel}
      pageRangeDisplayed={pageRangeDisplayed}
      marginPagesDisplayed={marginPagesDisplayed}
      containerClassName={classNames(containerClassName, styles.container)}
      pageClassName={classNames(pageClassName, styles.button, styles.page)}
      breakClassName={classNames(breakClassName, styles.button, styles.break)}
      activeClassName={classNames(activeClassName, styles.active)}
      previousClassName={classNames(previousClassName, styles.button, styles.previous)}
      nextClassName={classNames(nextClassName, styles.button, styles.next)}
      {...remainingProps}
    />
  );
};
