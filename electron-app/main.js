const path = require("path");
const { app, BrowserWindow, ipcMain } = require("electron");
const robot = require("robotjs");
const { linear } = require("everpolate");

let pX = 0;
let pY = 0;
let cX = 0;
let cY = 0;

const createWindow = () => {
  const win = new BrowserWindow({
    width: 640,
    height: 480,
    webPreferences: {
      nodeIntegration: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });
  // robot.setMouseDelay(1);
  ipcMain.on("moveMouse", (event, x, y) => {
    // robot.moveMouseSmooth(x * 100, y * 100);

    console.log({ x, y });

    const screensize = robot.getScreenSize();
    const wCam = 640;
    const hCam = 480;
    const wScr = screensize.width;
    const hScr = screensize.height;
    const smoothening = 7;
    const frameR = 100;

    // x = x * 100;
    // y = y * 100;
    console.log({
      wScr,
      hScr,
    });

    let x1 = linear(x, (frameR, wCam - frameR), (0, wScr));
    let y1 = linear(y, (frameR, hCam - frameR), (0, hScr));

    console.log({
      x1,
      y1,
    });

    cX = pX + (x1 - pX) / smoothening;
    cY = pY + (y1 - pY) / smoothening;

    robot.moveMouse(cX, cY);

    pX = cX;
    pY = cY;
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
