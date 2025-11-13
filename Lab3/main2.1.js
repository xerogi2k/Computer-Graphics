const canvas = document.getElementById('canvas'); 
const ctx = canvas.getContext('2d');

let stageSize = { width: window.innerWidth, height: window.innerHeight };
let position = { x: stageSize.width / 2, y: stageSize.height / 2 };
let isDragging = false;
let dragStart = { x: 0, y: 0 };
const initialSize = { width: stageSize.width, height: stageSize.height };

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  stageSize = { width: window.innerWidth, height: window.innerHeight };
  draw();
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

canvas.addEventListener('mousedown', (e) => {
  isDragging = true;
  dragStart = { x: e.offsetX, y: e.offsetY };
});

canvas.addEventListener('mousemove', (e) => {
  if (isDragging) {
    const dx = e.offsetX - dragStart.x;
    const dy = e.offsetY - dragStart.y;
    position.x += dx;
    position.y += dy;
    dragStart = { x: e.offsetX, y: e.offsetY };
    draw();
  }
});

canvas.addEventListener('mouseup', () => {
  isDragging = false;
});

function draw() {
  const { width, height } = stageSize;
  const { x, y } = position;

  ctx.clearRect(0, 0, width, height);
  ctx.save();
  ctx.translate(x, y);

  const scaleX = width / initialSize.width;
  const scaleY = height / initialSize.height;
  const scale = Math.min(scaleX, scaleY);
  ctx.scale(scale, scale);

  drawHedgehog(ctx);

  ctx.restore();
}

function drawHedgehog(ctx) {
  drawSpikes(ctx);
  drawEars(ctx);
  drawHands(ctx);
  drawFeet(ctx);
  drawBody(ctx);
  drawEyes(ctx);
  drawGlasses(ctx);
  drawEyebrows(ctx);
  drawMouth(ctx);
  drawNose(ctx);
}

function drawBody(ctx) {
  ctx.beginPath();
  ctx.arc(0, 0, 90, 0, Math.PI * 2);
  ctx.fillStyle = '#cc4b8e';
  ctx.fill();
  ctx.strokeStyle = '#aa3c76';
  ctx.lineWidth = 3;
  ctx.stroke();
}

function drawSpikes(ctx) {
  const spikeCount = 9;
  const radius = 150; // Увеличил для правильной логики отрисовки иголок
  const spikeLength = 80; // Длину и ширину тоже увеличил, чтобы подсчет был верным
  const spikeWidth = 100;
  
  ctx.fillStyle = '#502379';
// Индексы иголок для верхней половины (симметрично)
  const topSpikeIndices = [0, 1, 2, 7, 8]; // Индексы: верхняя + 2 справа + 2 слева

  for (let j = 0; j < topSpikeIndices.length; j++) {
    const i = topSpikeIndices[j];
    const angle = ((Math.PI * 2) / spikeCount) * i - Math.PI / 2;

    ctx.save();
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(radius, 0);
    ctx.lineTo(radius - spikeLength, -spikeWidth / 2);
    ctx.lineTo(radius - spikeLength, spikeWidth / 2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }
}

function drawEars(ctx) {
  ctx.fillStyle = '#cc4b8e';
  ctx.beginPath();
  ctx.arc(-90, -25, 10, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#aa3c76';
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(90, -25, 10, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#aa3c76';
  ctx.lineWidth = 3;
  ctx.stroke();
}

function drawHands(ctx) {
  ctx.fillStyle = '#cc4b8e';

  ctx.beginPath();
  ctx.ellipse(-75, 40, 10, 25, Math.PI / 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#aa3c76';
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.beginPath();
  ctx.ellipse(75, 40, 10, 25, -Math.PI / 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#aa3c76';
  ctx.lineWidth = 3;
  ctx.stroke();
}

function drawFeet(ctx) {
  ctx.fillStyle = '#cc4b8e';

  ctx.beginPath();
  ctx.ellipse(-25, 90, 15, 20, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#aa3c76';
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.beginPath();
  ctx.ellipse(25, 90, 15, 20, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#aa3c76';
  ctx.lineWidth = 3;
  ctx.stroke();
}

function drawEyes(ctx) {
  const eyeOffsetX = 25;
  const eyeOffsetY = -20;
  const eyeRadius = 16;

  ctx.fillStyle = 'white';
  ctx.beginPath();
  ctx.arc(-eyeOffsetX, eyeOffsetY, eyeRadius, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(eyeOffsetX, eyeOffsetY, eyeRadius, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = 'black';
  ctx.beginPath();
  ctx.arc(-eyeOffsetX, eyeOffsetY, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(eyeOffsetX, eyeOffsetY, 5, 0, Math.PI * 2);
  ctx.fill();
}

function drawGlasses(ctx) {
  ctx.strokeStyle = '#3b0f55';
  ctx.lineWidth = 6;

  // Оправа линз
  ctx.beginPath();
  ctx.arc(-25, -20, 20, 0, Math.PI * 2);
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(25, -20, 20, 0, Math.PI * 2);
  ctx.stroke();

  // Соединение линз
  ctx.beginPath();
  ctx.moveTo(-5, -20);
  ctx.lineTo(5, -20);
  ctx.stroke();

  // Душки очков
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(-45, -20);
  ctx.lineTo(-65, -25);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(45, -20);
  ctx.lineTo(65, -25);
  ctx.stroke();
}

function drawEyebrows(ctx) {
  ctx.strokeStyle = '#a2325b';
  ctx.lineWidth = 3;

  ctx.beginPath();
  ctx.moveTo(-35, -40);
  ctx.lineTo(-15, -45);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(15, -45);
  ctx.lineTo(35, -40);
  ctx.stroke();
}

function drawMouth(ctx) {
  ctx.beginPath();
  ctx.moveTo(-10, 30);
  ctx.quadraticCurveTo(0, 38, 10, 30);
  ctx.strokeStyle = '#3a0c2a';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function drawNose(ctx) {
  ctx.fillStyle = '#6d183e';
  ctx.beginPath();
  ctx.arc(0, 0, 7, 0, Math.PI * 2);
  ctx.fill();
}