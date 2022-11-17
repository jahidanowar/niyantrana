const path = require("path");
const { app, BrowserWindow, ipcMain } = require("electron");
const robot = require("robotjs");

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });
  // robot.setMouseDelay(1);
  ipcMain.on("moveMouse", (event, x, y) => {
    // robot.moveMouseSmooth(x * 100, y * 100);

    const screensize = robot.getScreenSize();

    x = x * 100;
    y = y * 100;

    // x1 is the x percentage of the screen width
    // y1 is the y percentage of the screen height
    const x1 = Math.round((x / 100) * screensize.width);
    const y1 = Math.round((y / 100) * screensize.height);

    // Smoothly move the mouse across the screen.
    // robot.moveMouseSmooth(x1, y1);

    robot.moveMouse(x1, y1);
  });

  ipcMain.on("mouseClick", (event) => {
    robot.mouseClick();

    console.log("Clicked");
  });

  win.loadFile("index.html");
};

app.whenReady().then(createWindow);
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
