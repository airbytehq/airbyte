export const Navattic = (props) => {
  return (
    <div
      style={{
        position: "relative",
        marginBottom: "1em",
        paddingBottom: props.paddingBottom,
        height: 0,
      }}
    >
      <iframe
        src={`https://capture.navattic.com/${props.id}`}
        title={props.title}
        loading="lazy"
        allowFullScreen
        allow="fullscreen"
        data-navattic-demo-id={props.id}
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
