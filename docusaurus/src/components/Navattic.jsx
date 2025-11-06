export const Navattic = (props) => {
  const { id, title, paddingBottom, aspectRatio = "16 / 9", height } = props;

  const containerStyle = {
    position: "relative",
    marginBottom: "1em",
    width: "100%",
  };

  if (height) {
    containerStyle.height = height;
  } else if (paddingBottom) {
    containerStyle.paddingBottom = paddingBottom;
    containerStyle.height = 0;
  } else {
    containerStyle.aspectRatio = aspectRatio;
  }

  return (
    <div style={containerStyle}>
      <iframe
        src={`https://capture.navattic.com/${id}`}
        title={title}
        loading="lazy"
        allowFullScreen
        allow="fullscreen"
        data-navattic-demo-id={id}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          border: "none",
          colorScheme: "light",
        }}
      />
    </div>
  );
};
