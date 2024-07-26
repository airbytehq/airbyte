export const YouTube = (props) => {
    return (
        <div style={{ position: "relative", marginBottom: "1em", paddingBottom: props.paddingBottom, height: 0}}>
            <iframe width="560" height="315" src={`https://www.youtube.com/embed/${props.id}`} title={props.title} frameborder="0" loading="lazy" allowFullScreen style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", colorScheme: "light"}} />
        </div>
    );
};
