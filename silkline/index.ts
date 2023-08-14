import * as pulumi from "@pulumi/pulumi";
import { createRepo } from "./image-repo";
import { createImage } from "./image";

const namePrefix = "airbyte-connectors";

const repo = createRepo(namePrefix);

// Add the name of all future sources here.
const sources = ["source-first-resonance-ion"];

const createFullPath = (sourcePath: string) =>
  `../airbyte-integrations/connectors/${sourcePath}`;

const images = sources.map((sourcePath) => {
  // TODO: Create full path
  const fullPath = createFullPath(sourcePath);
  // TODO create and return image.
  const image = createImage(sourcePath, repo.url, fullPath);

  return image;
});

export const imagePaths = pulumi.interpolate`${images.map(
  (image) => image.imageUri
)}`;
