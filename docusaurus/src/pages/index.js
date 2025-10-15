import React from 'react';
import Layout from '@theme/Layout';
import styles from './index.module.css';
import { Arcade } from '../components/Arcade';

export default function Home() {
  const navLinks = [
    {
      title: 'Platform',
      link: '/platform/',
      description: 'Deploy Airbyte locally, to cloud providers, or use Airbyte Cloud. Create connections, build custom connectors, and start syncing data in minutes.',
    },
    {
      title: 'Connectors',
      link: '/integrations/',
      description: 'Browse Airbyte\'s catalog of over 600 sources and destinations, and learn to set them up in Airbyte.',
    },
    {
      title: 'Release Notes',
      link: '/release_notes/',
      description: 'See what\'s new. Airbyte releases new Self-Managed versions regularly. Airbyte Cloud customers always have the latest enhancements.',
    },
    {
      title: 'AI Agents',
      link: '/ai-agents/',
      description: 'Explore AI Agent tools and capabilities for building intelligent data pipelines.',
    },
    {
      title: 'Placeholder Section 1',
      link: '#',
      description: 'This is a placeholder section that will be populated with content later.',
    },
    {
      title: 'Placeholder Section 2',
      link: '#',
      description: 'This is a placeholder section that will be populated with content later.',
    },
  ];

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
            {navLinks.map((item, index) => (
              <a 
                key={index} 
                href={item.link} 
                className={styles.navCard}
              >
                <div className={styles.navIcon}>
                  <PlaceholderIcon />
                </div>
                <h3 className={styles.navTitle}>{item.title}</h3>
                <p className={styles.navDescription}>{item.description}</p>
              </a>
            ))}
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
