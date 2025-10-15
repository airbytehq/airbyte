import React from 'react';
import Layout from '@theme/Layout';
import styles from './index.module.css';
import { Arcade } from '../components/Arcade';

export default function Home() {
  const PlatformIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      clipRule="evenodd"
      fillRule="evenodd"
      strokeLinejoin="round"
      strokeMiterlimit="2"
      xmlns="http://www.w3.org/2000/svg"
      className={styles.navIconSvg}
    >
      <path d="m21 9.005h-18v10.995c0 .621.52 1 1 1h16c.478 0 1-.379 1-1zm-18-1h18v-4.005c0-.478-.379-1-1-1h-16c-.62 0-1 .519-1 1zm15.25-3.25c.414 0 .75.336.75.75s-.336.75-.75.75-.75-.336-.75-.75.336-.75.75-.75zm-3 0c.414 0 .75.336.75.75s-.336.75-.75.75-.75-.336-.75-.75.336-.75.75-.75z" fillRule="nonzero"/>
    </svg>
  );

  const ConnectorsIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      fillRule="evenodd"
      clipRule="evenodd"
      className={styles.navIconSvg}
    >
      <path d="M12 0c6.623 0 12 5.377 12 12s-5.377 12-12 12-12-5.377-12-12 5.377-12 12-12zm0 2c5.519 0 10 4.481 10 10s-4.481 10-10 10-10-4.481-10-10 4.481-10 10-10zm2 12v-3l5 4-5 4v-3h-9v-2h9zm-4-6v-3l-5 4 5 4v-3h9v-2h-9z"/>
    </svg>
  );

  const ReleaseNotesIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      fillRule="evenodd"
      clipRule="evenodd"
      className={styles.navIconSvg}
    >
      <path d="M22 24h-20v-24h14l6 6v18zm-7-23h-12v22h18v-16h-6v-6zm3 15v1h-12v-1h12zm0-3v1h-12v-1h12zm0-3v1h-12v-1h12zm-2-4h4.586l-4.586-4.586v4.586z"/>
    </svg>
  );

  const AIAgentsIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 16 16"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      className={styles.navIconSvg}
    >
      <path fill="currentColor" d="m11.27 8.345-3.006-.458-1.346-2.72a.67.67 0 0 0-.602-.373.66.66 0 0 0-.573.372L4.397 7.887l-3.007.458c-.544.058-.744.745-.343 1.117l2.148 2.12-.516 3.007c-.057.4.286.744.659.744.114 0 .2 0 .315-.057l2.692-1.432 2.663 1.432c.115.057.2.057.315.057a.657.657 0 0 0 .659-.744l-.515-3.007 2.176-2.12c.372-.372.172-1.06-.372-1.117m-2.777 2.263-.516.487.115.716.286 1.575-1.403-.745-.63-.343-.659.343-1.403.745.286-1.575.115-.716-.516-.487L3.023 9.49l1.575-.23.716-.114 1.03-2.062.688 1.432.315.63.716.115 1.575.229zm1.976-5.356.745-1.517 1.546-.774-1.546-.744L10.469.67l-.773 1.547-1.518.744 1.518.774zm4.124.917-.458-.917-.459.917-.916.458.916.458.459.917.458-.917.916-.458z"/>
    </svg>
  );

  const PlaceholderIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="48" height="48" rx="8" fill="var(--ifm-color-primary-lightest)" />
      <path
        d="M24 14L28 18H26V28H22V18H20L24 14Z"
        fill="var(--ifm-color-primary)"
      />
      <path
        d="M16 32H32V34H16V32Z"
        fill="var(--ifm-color-primary)"
      />
    </svg>
  );

  const navLinks = [
    {
      title: 'Platform',
      link: '/platform/',
      description: 'Deploy Airbyte locally, to cloud providers, or use Airbyte Cloud. Create connections, build custom connectors, and start syncing data in minutes.',
      icon: PlatformIcon,
    },
    {
      title: 'Connectors',
      link: '/integrations/',
      description: 'Browse Airbyte\'s catalog of over 600 sources and destinations, and learn to set them up in Airbyte.',
      icon: ConnectorsIcon,
    },
    {
      title: 'Release Notes',
      link: '/release_notes/',
      description: 'See what\'s new. Airbyte releases new Self-Managed versions regularly. Airbyte Cloud customers always have the latest enhancements.',
      icon: ReleaseNotesIcon,
    },
    {
      title: 'AI Agents',
      link: '/ai-agents/',
      description: 'Explore AI Agent tools and capabilities for building intelligent data pipelines.',
      icon: AIAgentsIcon,
    },
    {
      title: 'Placeholder Section 1',
      link: '#',
      description: 'This is a placeholder section that will be populated with content later.',
      icon: PlaceholderIcon,
    },
    {
      title: 'Placeholder Section 2',
      link: '#',
      description: 'This is a placeholder section that will be populated with content later.',
      icon: PlaceholderIcon,
    },
  ];

  return (
    <Layout
      title="Airbyte documentation"
      description="Airbyte is an open source data integration and activation platform. It helps you consolidate data from hundreds of sources into your data warehouses, data lakes, and databases."
    >
      <div className={styles.homePage}>
        {/* Section 1: Hero with purple background */}
        <section className={styles.heroSection}>
          <div className={styles.heroContainer}>
            <div className={styles.heroLeft}>
              <h1 className={styles.heroTitle}>Airbyte documentation</h1>
              <p className={styles.heroDescription}>
                Airbyte is an open source data integration and activation platform. 
                It helps you consolidate data from hundreds of sources into your data 
                warehouses, data lakes, and databases. Then, it helps you move data 
                from those locations into the operational tools where work happens, 
                like CRMs, marketing platforms, and support systems.
              </p>
            </div>
            <div className={styles.heroRight}>
              <Arcade 
                id="8UUaeQOILatZ38Rjh8cs" 
                title="Airbyte Demo: Get Started Creating Connections" 
                paddingBottom="calc(61.416666666666664% + 41px)" 
              />
            </div>
          </div>
        </section>

        {/* Section 2: Navigation Links */}
        <section className={styles.navSection}>
          <div className={styles.navGrid}>
            {navLinks.map((item, index) => {
              const IconComponent = item.icon;
              return (
                <a 
                  key={index} 
                  href={item.link} 
                  className={styles.navCard}
                >
                  <div className={styles.navIcon}>
                    <IconComponent />
                  </div>
                  <h3 className={styles.navTitle}>{item.title}</h3>
                  <p className={styles.navDescription}>{item.description}</p>
                </a>
              );
            })}
          </div>
        </section>

        {/* Section 3: Why Airbyte */}
        <section className={styles.whySection}>
          <h2 className={styles.whyTitle}>Why Airbyte?</h2>
          <p className={styles.whyIntro}>
            Teams and organizations need efficient and timely data access to an 
            ever-growing list of data sources. In-house data pipelines are brittle 
            and costly to build and maintain. Airbyte's unique open source approach 
            enables your data stack to adapt as your data needs evolve.
          </p>
          <ul className={styles.whyList}>
            <li>
              <strong>Wide connector availability:</strong> Airbyte's connector 
              catalog comes "out-of-the-box" with over 600 pre-built connectors. 
              These connectors can be used to start replicating data from a source 
              to a destination in just a few minutes.
            </li>
            <li>
              <strong>Long-tail connector coverage:</strong> You can easily extend 
              Airbyte's capability to support your custom use cases through Airbyte's{' '}
              <a href="/platform/connector-development/connector-builder-ui/overview">
                No-Code Connector Builder
              </a>.
            </li>
            <li>
              <strong>Robust platform</strong> provides horizontal scaling required 
              for large-scale data movement operations, available as{' '}
              <a href="https://airbyte.com/product/airbyte-cloud">Cloud-managed</a> or{' '}
              <a href="https://airbyte.com/product/airbyte-enterprise">Self-managed</a>.
            </li>
            <li>
              <strong>Accessible User Interfaces</strong> through the UI,{' '}
              <a href="/platform/using-airbyte/pyairbyte/getting-started"><strong>PyAirbyte</strong></a>{' '}
              (Python library),{' '}
              <a href="/platform/api-documentation"><strong>API</strong></a>, and{' '}
              <a href="/platform/terraform-documentation"><strong>Terraform Provider</strong></a>{' '}
              to integrate with your preferred tooling and approach to infrastructure management.
            </li>
          </ul>
          <p className={styles.whyFooter}>
            Airbyte is suitable for a wide range of data integration use cases, 
            including AI data infrastructure and EL(T) workloads. Airbyte is also{' '}
            <a href="https://airbyte.com/product/powered-by-airbyte">embeddable</a>{' '}
            within your own app or platform to power your product.
          </p>
          <div className={styles.badges}>
            <a href="https://GitHub.com/airbytehq/airbyte/stargazers/">
              <img 
                src="https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000" 
                alt="GitHub stars" 
              />
            </a>{' '}
            <a href="https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md">
              <img 
                src="https://img.shields.io/static/v1?label=license&message=MIT&color=brightgreen" 
                alt="License" 
              />
            </a>{' '}
            <a href="https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md">
              <img 
                src="https://img.shields.io/static/v1?label=license&message=ELv2&color=brightgreen" 
                alt="License" 
              />
            </a>
          </div>
        </section>
      </div>
    </Layout>
  );
}
