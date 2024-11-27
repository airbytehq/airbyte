import Head from "@docusaurus/Head";

export const DocMetaTags = (props) => {
  const { title, description } = props;
  return (
    <Head>
      <title>{title}</title>
      <meta name="description" content={description} />
    </Head>
  );
};
