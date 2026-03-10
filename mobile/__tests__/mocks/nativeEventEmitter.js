module.exports = class NativeEventEmitter {
  addListener() {
    return { remove: () => {},};
  }
    removeAllListeners() {}
};