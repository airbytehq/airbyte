import React from 'react';
import Layout from '@theme/Layout';
import styles from './index.module.css';

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
      <path d="M12 0c6.623 0 12 5.377 12 12s-5.377 12-12 12-12-5.377-12-12 5.377-12 12-12zm2.085 14h-9v2h9v3l5-4-5-4v3zm-4-6v-3l-5 4 5 4v-3h9v-2h-9z"/>
    </svg>
  );

  const ReleaseNotesIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      className={styles.navIconSvg}
    >
      <path d="M22 6h-6v-6l6 6zm-8 2v-8h-12v24h20v-16h-8z"/>
    </svg>
  );

  const DevelopersIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      className={styles.navIconSvg}
    >
      <path d="M24 10.935v2.131l-8 3.947v-2.23l5.64-2.783-5.64-2.79v-2.223l8 3.948zm-16 3.848l-5.64-2.783 5.64-2.79v-2.223l-8 3.948v2.131l8 3.947v-2.23zm7.047-10.783h-2.078l-4.011 16h2.073l4.016-16z"/>
    </svg>
  );

  const CommunityIcon = () => (
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      className={styles.navIconSvg}
    >
      <path d="M17.997 18h-11.995l-.002-.623c0-1.259.1-1.986 1.588-2.33 1.684-.389 3.344-.736 2.545-2.209-2.366-4.363-.674-6.838 1.866-6.838 2.491 0 4.226 2.383 1.866 6.839-.775 1.464.826 1.812 2.545 2.209 1.49.344 1.589 1.072 1.589 2.333l-.002.619zm4.811-2.214c-1.29-.298-2.49-.559-1.909-1.657 1.769-3.342.469-5.129-1.4-5.129-1.265 0-2.248.817-2.248 2.324 0 3.903 2.268 1.77 2.246 6.676h4.501l.002-.463c0-.946-.074-1.493-1.192-1.751zm-22.806 2.214h4.501c-.021-4.906 2.246-2.772 2.246-6.676 0-1.507-.983-2.324-2.248-2.324-1.869 0-3.169 1.787-1.399 5.129.581 1.099-.619 1.359-1.909 1.657-1.119.258-1.193.805-1.193 1.751l.002.463z"/>
    </svg>
  );

  const drNavLinks = [
    {
      title: 'Platform',
      link: '/platform/',
      description: 'Create connections, build custom connectors, and start syncing data in minutes.',
      icon: PlatformIcon,
    },
    {
      title: 'Connectors',
      link: '/integrations/',
      description: 'Browse over 600 sources and destinations, and learn to set them up.',
      icon: ConnectorsIcon,
    },
    {
      title: 'Release notes',
      link: '/release_notes/',
      description: 'See what\'s new. Self-Managed versions release regularly. Cloud customers always have the latest.',
      icon: ReleaseNotesIcon,
    },
    {
      title: 'Developers',
      link: '/developers',
      description: 'Interact with Airbyte programmatically using our API, Terraform provider, and more.',
      icon: DevelopersIcon,
    },
    {
      title: 'Community',
      link: '/community',
      description: 'Get help using, and contribute to, Airbyte.',
      icon: CommunityIcon,
    },
  ];

  return (
    <Layout
      title=""
      description="Airbyte is an open source data replication platform and context layer for AI agents. Move your data from hundreds of sources into warehouses, data lakes, and databases, and equip your agents to query, search, and act on your data in real time."
    >
      <div className={styles.homePage}>
        {/* Section 1: Hero */}
        <section className={styles.heroSection}>
          <div className={styles.heroContainer}>
            <h1 className={styles.heroTitle}>Airbyte documentation</h1>
            <p className={styles.heroDescription}>
              Airbyte is an open source data replication platform and context layer for AI agents.
              Move your data from hundreds of sources into warehouses, data lakes, and databases,
              and equip your agents to query, search, and act on your data in real time.
            </p>
          </div>
        </section>

        {/* Section 2: Connectors */}
        <section className={styles.drSection}>
          <div className={styles.sectionInner}>
            {/* Popular connectors */}
            <div className={styles.connectorsRow}>
              <div className={styles.connectorGroup}>
                <h3 className={styles.drPopularTitle}>Popular sources</h3>
                <div className={styles.connectorButtons}>
                  <a href="/integrations/sources/postgres" className={styles.connectorButton} aria-label="Postgres" title="Postgres">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-postgres/latest/icon.svg" alt="Postgres" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/sources/facebook-marketing" className={styles.connectorButton} aria-label="Facebook Marketing" title="Facebook Marketing">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-facebook-marketing/latest/icon.svg" alt="Facebook Marketing" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/sources/salesforce" className={styles.connectorButton} aria-label="Salesforce" title="Salesforce">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-salesforce/latest/icon.svg" alt="Salesforce" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/sources/mysql" className={styles.connectorButton} aria-label="MySQL" title="MySQL">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-mysql/latest/icon.svg" alt="MySQL" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/sources/google-sheets" className={styles.connectorButton} aria-label="Google Sheets" title="Google Sheets">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-google-sheets/latest/icon.svg" alt="Google Sheets" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/sources/linkedin-ads" className={styles.connectorButton} aria-label="LinkedIn Ads" title="LinkedIn Ads">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-linkedin-ads/latest/icon.svg" alt="LinkedIn Ads" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/sources/mssql" className={styles.connectorButton} aria-label="MSSQL" title="MSSQL">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-mssql/latest/icon.svg" alt="MSSQL" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/sources/s3" className={styles.connectorButton} aria-label="S3" title="S3">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/source-s3/latest/icon.svg" alt="S3" className={styles.connectorIcon} />
                  </a>
                </div>
              </div>
              <div className={styles.connectorGroup}>
                <h3 className={styles.drPopularTitle}>Popular destinations</h3>
                <div className={styles.connectorButtons}>
                  <a href="/integrations/destinations/s3" className={styles.connectorButton} aria-label="S3" title="S3">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-s3/latest/icon.svg" alt="S3" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/destinations/postgres" className={styles.connectorButton} aria-label="Postgres" title="Postgres">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-postgres/latest/icon.svg" alt="Postgres" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/destinations/snowflake" className={styles.connectorButton} aria-label="Snowflake" title="Snowflake">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-snowflake/latest/icon.svg" alt="Snowflake" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/destinations/bigquery" className={styles.connectorButton} aria-label="BigQuery" title="BigQuery">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-bigquery/latest/icon.svg" alt="BigQuery" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/destinations/databricks" className={styles.connectorButton} aria-label="Databricks" title="Databricks">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-databricks/latest/icon.svg" alt="Databricks" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/destinations/s3-data-lake" className={styles.connectorButton} aria-label="S3 Data Lake" title="S3 Data Lake">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-s3-data-lake/latest/icon.svg" alt="S3 Data Lake" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/destinations/clickhouse" className={styles.connectorButton} aria-label="ClickHouse" title="ClickHouse">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-clickhouse/latest/icon.svg" alt="ClickHouse" className={styles.connectorIcon} />
                  </a>
                  <a href="/integrations/destinations/mssql" className={styles.connectorButton} aria-label="MSSQL" title="MSSQL">
                    <img src="https://connectors.airbyte.com/files/metadata/airbyte/destination-mssql/latest/icon.svg" alt="MSSQL" className={styles.connectorIcon} />
                  </a>
                </div>
              </div>
            </div>

            {/* DR navigation cards */}
            <div className={styles.drNavGrid}>
              {drNavLinks.map((item, index) => {
                const IconComponent = item.icon;
                return (
                  <a
                    key={index}
                    href={item.link}
                    className={styles.drNavCard}
                  >
                    <div className={styles.drNavIcon}>
                      <IconComponent />
                    </div>
                    <h3 className={styles.drNavTitle}>{item.title}</h3>
                    <p className={styles.drNavDescription}>{item.description}</p>
                  </a>
                );
              })}
            </div>

          </div>
        </section>

        {/* GitHub Badges */}
        <section className={styles.badgesSection}>
          <div className={styles.badgesContainer}>
            <a href="https://GitHub.com/airbytehq/airbyte/stargazers/">
              <img 
                src="https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star" 
                alt="GitHub stars" 
              />
            </a>{' '}
            <a href="/community/licenses/mit-license">
              <img 
                src="https://img.shields.io/static/v1?label=license&message=MIT&color=brightgreen" 
                alt="MIT License" 
              />
            </a>{' '}
            <a href="/community/licenses/elv2-license">
              <img 
                src="https://img.shields.io/static/v1?label=license&message=ELv2&color=brightgreen" 
                alt="ELv2 License" 
              />
            </a>
          </div>
        </section>
      </div>
    </Layout>
  );
}
