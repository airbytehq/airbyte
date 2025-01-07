import LiteYouTubeEmbed from "react-lite-youtube-embed";
import "react-lite-youtube-embed/dist/LiteYouTubeEmbed.css";

export const YoutubeEmbed = ({ id, title }) => {
  return (
    <LiteYouTubeEmbed
      id={id}
      title={title}
      poster="maxresdefault"
    />
  );
};
