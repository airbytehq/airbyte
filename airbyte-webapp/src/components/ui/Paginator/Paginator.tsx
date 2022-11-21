import classNames from "classnames";
import ReactPaginate from "react-paginate";

import styles from "./Paginator.module.scss";

interface PaginatorProps {
  className?: string;
  numPages: number;
  onPageChange: (selectedPageIndex: number) => void;
  selectedPage: number;
}

// this keeps the number of elements displayed constant regardless of which page is selected
function pageRangeDisplayed(numPages: number, selectedPageIndex: number): number {
  if (selectedPageIndex === 0 || numPages - selectedPageIndex <= 3) {
    return 6;
  } else if (selectedPageIndex === 1 || selectedPageIndex === 2) {
    return 5;
  } else if (selectedPageIndex === 3 || numPages - selectedPageIndex === 4) {
    return 4;
  }
  return 3;
}

export const Paginator: React.FC<PaginatorProps> = ({ className, numPages, onPageChange, selectedPage }) => (
  <ReactPaginate
    pageCount={numPages}
    onPageChange={(event) => {
      onPageChange(event.selected);
    }}
    forcePage={selectedPage}
    breakLabel="…"
    nextLabel=">"
    previousLabel="<"
    pageRangeDisplayed={pageRangeDisplayed(numPages, selectedPage)}
    marginPagesDisplayed={2}
    containerClassName={classNames(className, styles.container)}
    pageClassName={classNames(styles.button, styles.page)}
    breakClassName={classNames(styles.button, styles.break)}
    activeClassName={styles.active}
    previousClassName={classNames(styles.button, styles.previous)}
    nextClassName={classNames(styles.button, styles.next)}
  />
);
