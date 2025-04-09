export const intervalProvider = {
    setInterval(...args) {
        const { delegate } = intervalProvider;
        return ((delegate === null || delegate === void 0 ? void 0 : delegate.setInterval) || setInterval)(...args);
    },
    clearInterval(handle) {
        const { delegate } = intervalProvider;
        return ((delegate === null || delegate === void 0 ? void 0 : delegate.clearInterval) || clearInterval)(handle);
    },
    delegate: undefined,
};
//# sourceMappingURL=intervalProvider.js.map