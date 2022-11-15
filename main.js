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
    // robot.moveMouse(x * 100, y * 100);
    // console.log(x * 100, y * 100);

    // robot.moveMouseSmooth(x * 100, y * 100);

    const screensize = robot.getScreenSize();

    const x1 = Math.round(x * screensize.width);
    const y1 = Math.round(y * screensize.height);

    console.log(x1, y1);

    // Smoothly move the mouse across the screen.
    robot.moveMouseSmooth(x1, y1);

    // robot.moveMouse(x1, y1);
  });

  ipcMain.on("mouseClick", (event) => {
    robot.mouseClick();

    console.log("Clicked");
  });

  win.loadFile("index.html");
};

app.whenReady().then(createWindow);
