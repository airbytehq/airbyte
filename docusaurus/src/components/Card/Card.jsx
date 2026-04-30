import {
  faArrowRight,
  faBook,
  faCloud,
  faDownload,
  faGear,
  faLightbulb,
  faLock,
  faPlug,
  faPuzzlePiece,
  faRobot,
  faRocket,
} from "@fortawesome/free-solid-svg-icons";
import { faPython } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styles from "./Card.module.css";
import { CloudIcon, EnterpriseIcon, OssIcon } from "./CustomIcons";

const FA_ICONS = {
  "fa-book": faBook,
  "fa-cloud": faCloud,
  "fa-download": faDownload,
  "fa-gear": faGear,
  "fa-lightbulb": faLightbulb,
  "fa-lock": faLock,
  "fa-plug": faPlug,
  "fa-puzzle-piece": faPuzzlePiece,
  "fa-python": faPython,
  "fa-robot": faRobot,
  "fa-rocket": faRocket,
};

const CUSTOM_ICONS = {
  cloud: CloudIcon,
  enterprise: EnterpriseIcon,
  oss: OssIcon,
};

const Link = ({ children, href, variant = "primary" }) => {
  const linkClass =
    variant === "secondary" ? styles.cardCtaSecondary : styles.cardCtaPrimary;

  return (
    <a className={`${styles.cardCta} ${linkClass}`} href={href}>
      {children}
      <FontAwesomeIcon icon={faArrowRight} />
    </a>
  );
};

const Icon = ({ name }) => {
  const IconComponent = FA_ICONS[name] || CUSTOM_ICONS[name];
  if (name in FA_ICONS) {
    return <FontAwesomeIcon icon={FA_ICONS[name]} />;
  }
  if (name in CUSTOM_ICONS) {
    return <IconComponent />;
  }
  return null;
};

export const CardWithIcon = ({
  title,
  description,
  ctaText,
  ctaLink,
  ctaVariant = "primary",
  icon,
}) => {
  return (
    <div className={styles.card}>
      <div className={styles.cardContent}>
        {icon && (
          <div className={styles.cardIcon}>
            <Icon name={icon} />
          </div>
        )}
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {ctaText && (
        <Link href={ctaLink} variant={ctaVariant}>
          {ctaText}
        </Link>
      )}
    </div>
  );
};
