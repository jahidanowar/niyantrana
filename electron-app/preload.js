const { contextBridge, ipcRenderer } = require("electron");
// const robot = require("robotjs");

contextBridge.exposeInMainWorld("versions", {
  node: () => process.versions.node,
  chrome: () => process.versions.chrome,
  electron: () => process.versions.electron,
  // we can also expose variables, not just functions
});

contextBridge.exposeInMainWorld("robot", {
  moveMouse: (x, y) => {
    ipcRenderer.send("moveMouse", x, y);
    // console.log(x, y);
  },
  mouseClick: () => ipcRenderer.send("mouseClick"),
});
