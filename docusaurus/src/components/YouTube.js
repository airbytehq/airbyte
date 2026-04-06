import React from "react";

export default function YouTube({ id }) {
  return (
    <div style={{ marginBottom: "2rem" }}>
        <div style={{ position: "relative", paddingBottom: "56.25%", height: 0 }}>
        <iframe
            src={`https://www.youtube.com/embed/${id}`}
            style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            }}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            title="YouTube video"
        />
        </div>
    </div>
  );
}
