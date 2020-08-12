import React from "react";
import Link from "../../components/Link";
import { Routes } from "../routes";

const SourcesPage: React.FC = () => {
  return (
    <>
      <div>Main Sources Page</div>
      <br />
      <Link to={Routes.Preferences}>Go to Preferences Form</Link>
    </>
  );
};

export default SourcesPage;
