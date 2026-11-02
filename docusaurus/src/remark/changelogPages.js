const {
  CHANGELOG_PAGE_DOCS,
  getChangelogPages,
} = require("../scripts/connector-changelog-pages");

function getDocId(filePath) {
  const match = filePath
    .replace(/\\/g, "/")
    .match(/(?:^|\/)integrations\/(sources\/(?:postgres|hubspot))\.md$/);
  return match?.[1];
}

function changelogIntroduction(title, pages) {
  const latest = pages.find((page) => page.slug === "changelog");
  const olderPages = pages.filter((page) => page.slug !== "changelog");
  const children = [
    {
      type: "text",
      value: "To see this connector's version history, read the ",
    },
    {
      type: "link",
      url: `/integrations/${latest.id}`,
      children: [{ type: "text", value: `${title} changelog` }],
    },
    {
      type: "text",
      value: olderPages.length ? ". For older versions, see " : ".",
    },
  ];

  olderPages.forEach((page, index) => {
    if (index > 0) {
      children.push({
        type: "text",
        value: index === olderPages.length - 1 ? " and " : ", ",
      });
    }
    children.push({
      type: "link",
      url: `/integrations/${page.id}`,
      children: [{ type: "text", value: page.rangeLabel }],
    });
  });
  if (olderPages.length) {
    children.push({ type: "text", value: "." });
  }

  return { type: "paragraph", children };
}

function findChangelogHeading(nodes) {
  for (let index = 0; index < nodes.length; index += 1) {
    const node = nodes[index];
    const headingText = node.children
      ?.map((child) => child.value || "")
      .join("")
      .toLowerCase();
    if (
      node.type === "heading" &&
      node.depth === 2 &&
      headingText === "changelog"
    ) {
      return { siblings: nodes, index };
    }

    if (Array.isArray(node.children)) {
      const match = findChangelogHeading(node.children);
      if (match) return match;
    }
  }

  return null;
}

function plugin() {
  return (tree, file) => {
    const docId = getDocId(file.path);
    if (!docId || !CHANGELOG_PAGE_DOCS.includes(docId)) return;

    const pages = getChangelogPages(docId);
    const title = pages[0].title;
    const heading = findChangelogHeading(tree.children);
    if (!heading) return;

    let nextSectionIndex = heading.index + 1;
    while (nextSectionIndex < heading.siblings.length) {
      const node = heading.siblings[nextSectionIndex];
      if (node.type === "heading" && node.depth <= 2) break;
      nextSectionIndex += 1;
    }

    heading.siblings.splice(
      heading.index + 1,
      nextSectionIndex - heading.index - 1,
      changelogIntroduction(title, pages),
    );
  };
}

module.exports = plugin;
