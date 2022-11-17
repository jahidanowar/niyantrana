const information = document.getElementById("info");
information.innerText = `This app is using Chrome (v${versions.chrome()}), Node.js (v${versions.node()}), and Electron (v${versions.electron()})`;

const videoElement = document.getElementsByClassName("input_video")[0];
const canvasElement = document.getElementsByClassName("output_canvas")[0];
const pointerElement = document.getElementById("pointer");
const debugElement = document.getElementById("debug");
const canvasCtx = canvasElement.getContext("2d");
const clickSound = new Audio("./assets/audio/click.wav");

async function onResults(results) {
  //   console.log(results.multiHandLandmarks);
  const hand = results.multiHandLandmarks[0] || null;
  const indexFinger = hand && hand.length > 0 ? hand[8] : null;
  const middleFinger = hand && hand.length > 0 ? hand[12] : null;

  // Change the pointer position to the index finger position.
  //   console.log(indexFinger);
  if (indexFinger && middleFinger) {
    const { x: x1, y: y1 } = indexFinger;
    const { x: x2, y: y2 } = middleFinger;

    // Calculate the angle between the index finger and the middle finger.
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const angleDeg = (angle * 180) / Math.PI;

    // pointerElement.style.transform = `rotate(${angleDeg}deg)`;

    // Calculate the distance between the index finger and the middle finger.

    const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    debugElement.innerText = `${angleDeg} ${distance}`;

    debugElement.innerHTML = `<div class="text-center alert alert-info">
        <div> X1: ${x1 * 100}, Y1: ${y1 * 100}</div>
        <div> X2: ${x2 * 100}, Y2: ${y2 * 100}</div>
        <div> Angle: ${angleDeg}</div>
        <div> Distance: ${distance * 100}</div>
     </dvi>`;

    // Move the mouse pointer to the index finger position.
    await robot.moveMouse(x1, y1);

    // Only move the pointer if the distance is less than 8 i:e both finger touching.
    if (distance * 100 < 5.0) {
      console.log({
        distance: distance * 100,
      });
      // Change the color of the pointer to red.
      pointerElement.style.backgroundColor = "red";
      pointerElement.innerText = "Click";
      // PLay Click Sound
      //   clickSound.play();

      // robot.mouseClick();
    } else {
      // Change the color of the pointer to green.
      pointerElement.style.backgroundColor = "green";
      pointerElement.innerText = "";
    }
  }

  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  canvasCtx.drawImage(
    results.image,
    0,
    0,
    canvasElement.width,
    canvasElement.height
  );
  if (results.multiHandLandmarks) {
    for (const landmarks of results.multiHandLandmarks) {
      drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
        color: "#00FF00",
        lineWidth: 2,
      });
      drawLandmarks(canvasCtx, landmarks, {
        color: "#FF0000",
        lineWidth: 1,
      });
    }
  }
  canvasCtx.restore();
}

const hands = new Hands({
  locateFile: (file) => {
    // console.log({ file });
    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
  },
});
hands.setOptions({
  maxNumHands: 2,
  modelComplexity: 1,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5,
});
hands.onResults(onResults);

const camera = new Camera(videoElement, {
  onFrame: async () => {
    await hands.send({ image: videoElement });
  },
  width: 1920,
  height: 1080,
});
camera.start();
