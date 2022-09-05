import { faChevronLeft, faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import React, { useMemo } from "react";
import Slider, { CustomArrowProps, Settings as SliderProps } from "react-slick";

import { Text } from "components/base/Text";

import styles from "./SlickSlider.module.scss";

import "./slider.css";

interface SlickSliderProps {
  title?: string;
  sliderSettingsOverride?: SliderProps;
}

export const SlickSlider: React.FC<SlickSliderProps> = ({ title, sliderSettingsOverride, children }) => {
  const PrevArrow = ({ slideCount, currentSlide, className, onClick, ...restProps }: CustomArrowProps) => (
    <div
      className={classnames(styles.leftArrow, {
        [styles.arrowDisabled]: onClick === null,
      })}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label="previous slide"
      data-testid="previous-slide-btn"
    >
      <FontAwesomeIcon icon={faChevronLeft} className={classnames(className)} {...restProps} />
    </div>
  );
  const NextArrow = ({ slideCount, currentSlide, className, onClick, ...restProps }: CustomArrowProps) => (
    <div
      className={classnames(styles.rightArrow, {
        [styles.arrowDisabled]: onClick === null,
      })}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label="next slide"
      data-testid="next-slide-btn"
    >
      <FontAwesomeIcon icon={faChevronRight} className={classnames(className)} {...restProps} />
    </div>
  );

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
      ...sliderSettingsOverride,
    }),
    [sliderSettingsOverride]
  );

  return (
    <div className={styles.container}>
      <div className={styles.titleContainer}>{title && <Text size="sm">{title}</Text>}</div>
      <Slider {...settings}>{children}</Slider>
    </div>
  );
};
