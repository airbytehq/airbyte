import { faChevronLeft, faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import React, { useMemo } from "react";
import Slider, { CustomArrowProps, Settings as SliderProps } from "react-slick";

import { Text } from "components/ui/Text";

import styles from "./SlickSlider.module.scss";

import "./slider.css";

const PrevArrow = ({ slideCount, currentSlide, className, onClick, ...restProps }: CustomArrowProps) => (
  <button
    className={classnames(styles.leftArrow, {
      [styles.arrowDisabled]: onClick === null,
    })}
    onClick={onClick}
    tabIndex={0}
    type="button"
    aria-label="previous slide"
    data-testid="previous-slide-btn"
  >
    <FontAwesomeIcon icon={faChevronLeft} className={classnames(className)} {...restProps} />
  </button>
);
const NextArrow = ({ slideCount, currentSlide, className, onClick, ...restProps }: CustomArrowProps) => (
  <button
    className={classnames(styles.rightArrow, {
      [styles.arrowDisabled]: onClick === null,
    })}
    onClick={onClick}
    tabIndex={0}
    type="button"
    aria-label="next slide"
    data-testid="next-slide-btn"
  >
    <FontAwesomeIcon icon={faChevronRight} className={classnames(className)} {...restProps} />
  </button>
);

interface SlickSliderProps {
  title?: string;
  sliderSettings?: SliderProps;
  children: React.ReactNode;
}

export const SlickSlider: React.FC<SlickSliderProps> = ({ title, sliderSettings, children }) => {
  const settings: SliderProps = useMemo(
    () => ({
      arrows: true,
      accessibility: true,
      infinite: false,
      swipeToSlide: true,
      speed: 200,
      slidesToShow: 2,
      slidesToScroll: 2,
      prevArrow: <PrevArrow />,
      nextArrow: <NextArrow />,
      ...sliderSettings,
    }),
    [sliderSettings]
  );

  return (
    <div className={styles.container}>
      <div className={styles.titleContainer}>{title && <Text size="sm">{title}</Text>}</div>
      <Slider {...settings}>{children}</Slider>
    </div>
  );
};
