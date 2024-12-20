import { faArrowRight, faCloud, faDownload, faLock } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styles from "./Card.module.css";
import { CloudIcon, EnterpriseIcon, OssIcon } from "./CustomIcons";

const FA_ICONS = {
  "fa-cloud": faCloud,
  "fa-download": faDownload,
  "fa-lock": faLock,

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
    <div className={`${styles.cardCta} ${linkClass}`}>
      <a href={href}>{children}</a>
      <FontAwesomeIcon icon={faArrowRight} />
    </div>
  );
};

const Icon = ({ name }) => {
  const IconComponent = FA_ICONS[name] || CUSTOM_ICONS[name];
  if (name in FA_ICONS) {
    return (
      <FontAwesomeIcon icon={FA_ICONS[name]} />
    );
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
      {icon && <div className={styles.cardIcon}><Icon name={icon} /></div>}
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {ctaText && <Link href={ctaLink} variant={ctaVariant}>{ctaText}</Link>}
    </div>
  );
};
