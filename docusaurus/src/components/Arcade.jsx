export const Arcade = (props) => {
    return (
        <div style={{ position: "relative", marginBottom: "1em", paddingBottom: "calc(56.73828125% + 41px)", height: 0}}>
            <iframe src={`https://demo.arcade.software/${props.id}?embed`} title={props.title} frameborder="0" loading="lazy" allowFullScreen style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", colorScheme: "light"}} />
        </div>
    );
};