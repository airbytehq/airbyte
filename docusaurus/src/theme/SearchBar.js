import SearchBar from "@theme-original/SearchBar";
import React from "react";
import MarkpromptChat from "../components/MarkpromptChat/MarkpromptChat";

export default function SearchBarWrapper(props) {
  return (
    <div style={{ display: "flex", columnGap: "10px" }}>
      <MarkpromptChat />
      <SearchBar {...props} />
    </div>
  );
}
