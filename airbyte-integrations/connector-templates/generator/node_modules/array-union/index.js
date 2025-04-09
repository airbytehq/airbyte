const arrayUnion = (...arguments_) => [...new Set(arguments_.flat())];

export default arrayUnion;
