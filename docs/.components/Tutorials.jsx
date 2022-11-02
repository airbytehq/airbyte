import React from "react";

// for some reason, tailwind is not working here

// https://stackoverflow.com/questions/71223891/react-and-jsdoc-how-to-document-a-react-component-properly

/**
 * @typedef {object} Source
 * @property {string} name - source name
 * @property {string} link - source link
 * @property {string} logo - source logo
 */

/**
 * @typedef {object} Props
 * @property {Array<Source>} sources - sources
 * @property {string} title - Tutorial title
 * @property {string} category - Tutorial category
 * @property {string} description - Tutorial description
 * @property {string} publishedAt - Tutorial publishedAt
 */

const data = [
  {
    sources: [
      {
        name: "Postgres",
        link: "/connectors/postgresql-source",
        logo: "https://assets-global.website-files.com/6064b31ff49a2d31e0493af1/611221491f8f4ce4e5160b36_postgreSQL.svg",
      },
      {
        name: "Redshift",
        link: "/connectors/redshift-destination",
        logo: "https://assets-global.website-files.com/6064b31ff49a2d31e0493af1/6114a61fd0f73c0a55004429_amazon_redshift.svg",
      },
    ],
    title: "Replicate Postgres data to Redshift for analytics",
    url: "https://airbyte.com/tutorials/postgres-to-redshift-data-replication",
    category: "Engineering",
    description:
      "Learn how to build an ELT pipeline to replicate data from Postgres to Redshift in AWS.",
    publishedAt: "Oct 21, 2022",
  },
  {
    sources: [
      {
        name: "Postgres",
        link: "/connectors/postgresql-source",
        logo: "https://assets-global.website-files.com/6064b31ff49a2d31e0493af1/611221491f8f4ce4e5160b36_postgreSQL.svg",
      },
      {
        name: "Postgres",
        link: "/connectors/postgresql-source",
        logo: "https://assets-global.website-files.com/6064b31ff49a2d31e0493af1/611221491f8f4ce4e5160b36_postgreSQL.svg",
      },
    ],
    title: "Explore Airbyte's Change Data Capture (CDC) replication",
    url: "https://airbyte.com/tutorials/postgres-to-redshift-data-replication",
    category: "Engineering",
    description:
      "Learn how Airbyte’s Change Data Capture (CDC) synchronization replication works.",
    publishedAt: "Sep 29, 2022",
  },
  {
    sources: [
      {
        name: "Postgres",
        link: "/connectors/postgresql-source",
        logo: "https://assets-global.website-files.com/6064b31ff49a2d31e0493af1/611221491f8f4ce4e5160b36_postgreSQL.svg",
      },
      {
        name: "S3",
        link: "/connectors/s3-source",
        logo: "https://assets-global.website-files.com/6064b31ff49a2d31e0493af1/610d7333bf97521d40fce7a5_aws_s3.svg",
      },
    ],
    title: "Export Postgres data to CSV, JSON, Parquet and Avro files in S3",
    url: "https://airbyte.com/tutorials/postgres-to-redshift-data-replication",
    category: "Engineering",
    description:
      "Learn how to easily export Postgres data to CSV, JSON, Parquet, and Avro file formats stored in AWS S3.",
    publishedAt: "Sep 26, 2022",
  },
];

export default function Tutorials() {
  return data.map((tutorial, i) => <Tutorial key={i} {...tutorial} />);
}

/**
 * Tutorial component.
 *
 * @type {React.FC<Props>}
 * @returns {React.ReactElement} The component.
 */
export function Tutorial({
  sources,
  title,
  category,
  description,
  publishedAt,
  url,
}) {
  return (
    <div
      style={{
        WebkitBoxDirection: "normal",
        WebkitBoxOrient: "vertical",
        backgroundColor: "#FFFFFF",
        borderRadius: "12px",
        boxShadow: "rgba(26, 25, 77, 0.12) 0 2px 4px 0",
        boxSizing: "border-box",
        color: "#1A194D",
        display: "block",
        flexDirection: "column",
        fontFamily: '"Plus Jakarta Sans", sans-serif',
        fontSize: "18px",
        fontWeight: "500",
        height: "100%",
        lineHeight: "21.78px",
        position: "relative",
        textAlign: "left",
        textDecoration: "none",
        transition: "box-shadow .3s",
        width: "100%",
      }}
    >
      <div
        className="card-head"
        style={{
          backgroundColor: "#1A194D",
          borderTopLeftRadius: "12px",
          borderTopRightRadius: "12px",
          boxSizing: "border-box",
          color: "#1A194D",
          fontFamily: '"Plus Jakarta Sans", sans-serif',
          fontSize: "18px",
          fontWeight: "500",
          lineHeight: "21.78px",
          minHeight: "60px",
          textAlign: "left",
          textDecoration: "none",
        }}
      ></div>
      <div
        className="recipe-connectors-wrapper w-dyn-list"
        style={{
          boxSizing: "border-box",
          color: "#1A194D",
          fontFamily: '"Plus Jakarta Sans", sans-serif',
          fontSize: "18px",
          fontWeight: "500",
          lineHeight: "21.78px",
          marginTop: "-45px",
          paddingLeft: "24px",
          paddingRight: "24px",
          position: "relative",
          textAlign: "left",
          textDecoration: "none",
        }}
      >
        <div
          role="list"
          style={{
            WebkitBoxAlign: "center",
            alignItems: "center",
            boxSizing: "border-box",
            color: "#1A194D",
            display: "flex",
            fontFamily: '"Plus Jakarta Sans", sans-serif',
            fontSize: "18px",
            fontWeight: "500",
            lineHeight: "21.78px",
            textAlign: "left",
            textDecoration: "none",
          }}
        >
          {sources.map((source, i) => (
            <div
              key={i}
              role="listitem"
              className="w-dyn-item"
              style={{
                boxSizing: "border-box",
                color: "#1A194D",
                fontFamily: '"Plus Jakarta Sans", sans-serif',
                fontSize: "18px",
                fontWeight: "500",
                lineHeight: "21.78px",
                textAlign: "left",
                textDecoration: "none",
              }}
            >
              <a href={source.link} style={{ display: "inline-block" }}>
                <img
                  src={source.logo}
                  loading="lazy"
                  alt=""
                  style={{
                    backgroundColor: "#FFFFFF",
                    borderRadius: "50%",
                    boxShadow:
                      "rgba(26, 25, 77, 0.2) 0 81px 36px -51px, rgba(26, 25, 77, 0.12) 0 12px 24px 0",
                    boxSizing: "border-box",
                    color: "#FF6A4D",
                    display: "inline-block",
                    fontFamily: '"Plus Jakarta Sans", sans-serif',
                    fontSize: "18px",
                    fontWeight: "500",
                    height: "90px",
                    lineHeight: "21.78px",
                    marginRight: "14px",
                    maxWidth: "100%",
                    position: "relative",
                    textAlign: "left",
                    textDecoration: "none",
                    width: "90px",
                  }}
                />
              </a>
            </div>
          ))}
        </div>
      </div>
      <div
        className="card-body"
        style={{
          WebkitBoxFlex: "1",
          boxSizing: "border-box",
          color: "#1A194D",
          display: "block",
          flex: "1 1 0",
          fontFamily: '"Plus Jakarta Sans", sans-serif',
          fontSize: "18px",
          fontWeight: "500",
          lineHeight: "21.78px",
          padding: "1.5rem",
          position: "relative",
          textAlign: "left",
          textDecoration: "none",
          width: "100%",
        }}
      >
        <div
          className="mb-8 card-metadata-text"
          style={{
            WebkitBoxAlign: "center",
            alignItems: "center",
            boxSizing: "border-box",
            color: "#AFAFC1",
            display: "flex",
            fontFamily: "initial",
            fontSize: "14px",
            fontWeight: "initial",
            lineHeight: "1",
            marginBottom: "8px",
            textAlign: "initial",
          }}
        >
          10 minutes
        </div>
        <a href={url} className="link-block-plain w-inline-block">
          <h3
            style={{
              boxSizing: "border-box",
              color: "#1A194D",
              fontFamily: '"Plus Jakarta Sans", sans-serif',
              fontSize: "24px",
              fontWeight: "700",
              lineHeight: "29.05px",
              marginBottom: "10px",
              marginTop: "0",
              textAlign: "left",
              textDecoration: "none",
            }}
          >
            {title}
          </h3>
        </a>
        <div
          className="cms-item-tags"
          style={{
            WebkitBoxAlign: "center",
            alignItems: "center",
            boxSizing: "border-box",
            color: "#1A194D",
            display: "flex",
            fontFamily: '"Plus Jakarta Sans", sans-serif',
            fontSize: "18px",
            fontWeight: "500",
            lineHeight: "21.78px",
            marginBottom: "10px",
            marginLeft: "-3px",
            textAlign: "left",
            textDecoration: "none",
          }}
        >
          <div
            className="tutorials-version_component"
            style={{
              boxSizing: "border-box",
              color: "#1A194D",
              columnGap: ".3rem",
              display: "flex",
              fontFamily: '"Plus Jakarta Sans", sans-serif',
              fontSize: "18px",
              fontWeight: "500",
              lineHeight: "21.78px",
              marginRight: ".3rem",
              rowGap: ".3rem",
              textAlign: "left",
              textDecoration: "none",
            }}
          >
            <div
              className="tutorials-version_item w-condition-invisible"
              style={{
                WebkitBoxAlign: "center",
                WebkitBoxPack: "center",
                alignItems: "center",
                backgroundColor: "#F8F8FA",
                borderRadius: "50%",
                boxSizing: "border-box",
                color: "#1A194D",
                display: "none",
                fontFamily: '"Plus Jakarta Sans", sans-serif',
                fontSize: "18px",
                fontWeight: "500",
                height: "2.5rem",
                justifyContent: "center",
                lineHeight: "21.78px",
                textAlign: "left",
                textDecoration: "none",
                width: "2.5rem",
              }}
            >
              <img
                src="https://assets-global.website-files.com/605e01bc25f7e19a82e74788/62697f9bfaa483b7d0bdf496_open-source.png"
                loading="lazy"
                width="13"
                alt=""
                className="version-img"
                style={{
                  borderStyle: "initial",
                  borderWidth: "0",
                  boxSizing: "border-box",
                  color: "#1A194D",
                  display: "inline-block",
                  fontFamily: '"Plus Jakarta Sans", sans-serif',
                  fontSize: "18px",
                  fontWeight: "500",
                  height: "2rem",
                  lineHeight: "21.78px",
                  maxWidth: "100%",
                  textAlign: "left",
                  textDecoration: "none",
                  verticalAlign: "middle",
                  width: "2rem",
                }}
              />
            </div>
            <div
              className="tutorials-version_item"
              style={{
                WebkitBoxAlign: "center",
                WebkitBoxPack: "center",
                alignItems: "center",
                backgroundColor: "#F8F8FA",
                borderRadius: "50%",
                boxSizing: "border-box",
                color: "#1A194D",
                display: "flex",
                fontFamily: '"Plus Jakarta Sans", sans-serif',
                fontSize: "18px",
                fontWeight: "500",
                height: "2.5rem",
                justifyContent: "center",
                lineHeight: "21.78px",
                textAlign: "left",
                textDecoration: "none",
                width: "2.5rem",
              }}
            >
              <img
                src="https://assets-global.website-files.com/605e01bc25f7e19a82e74788/62697fa39a69e2ad4a9c2bae_cloud.png"
                loading="lazy"
                width="13"
                alt=""
                className="version-img"
                style={{
                  borderStyle: "initial",
                  borderWidth: "0",
                  boxSizing: "border-box",
                  color: "#1A194D",
                  display: "inline-block",
                  fontFamily: '"Plus Jakarta Sans", sans-serif',
                  fontSize: "18px",
                  fontWeight: "500",
                  height: "2rem",
                  lineHeight: "21.78px",
                  maxWidth: "100%",
                  textAlign: "left",
                  textDecoration: "none",
                  verticalAlign: "middle",
                  width: "2rem",
                }}
              />
            </div>
          </div>
          <a
            href="https://airbyte.com/tutorials?tutorial-categories=engineering"
            className="tag recipes-tag w-inline-block"
            style={{
              backgroundColor: "rgba(98, 94, 255, 0.1)",
              borderRadius: "25px",
              boxSizing: "border-box",
              color: "#625EFF",
              display: "block",
              fontFamily: '"Plus Jakarta Sans", sans-serif',
              fontSize: "14px",
              fontWeight: "500",
              lineHeight: "26px",
              marginRight: "8px",
              maxWidth: "100%",
              padding: "4px 12px",
              textAlign: "left",
              textDecoration: "none",
            }}
          >
            <div>{category}</div>
          </a>
        </div>
        <p
          className="text-3"
          style={{
            boxSizing: "border-box",
            color: "#1A194D",
            fontFamily: '"Plus Jakarta Sans", sans-serif',
            fontSize: "16px",
            fontWeight: "400",
            lineHeight: "137%",
            marginBottom: "10px",
            marginTop: "0",
            textAlign: "left",
            textDecoration: "none",
          }}
        >
          {description}
        </p>
        <div
          className="card-metadata-text w-embed"
          style={{
            WebkitBoxAlign: "center",
            alignItems: "center",
            boxSizing: "border-box",
            color: "#AFAFC1",
            display: "flex",
            fontFamily: '"Plus Jakarta Sans", sans-serif',
            fontSize: "14px",
            fontWeight: "500",
            lineHeight: "1",
            textAlign: "left",
            textDecoration: "none",
          }}
        >
          <span> Published on {publishedAt} </span>
        </div>
      </div>
    </div>
  );
}
