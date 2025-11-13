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

  drawShip(ctx);

  ctx.restore();
}

function drawShip(ctx) {
  const bigCircleRadius = 90;
  const mediumCircleRadius = 60;
  const smallCircleRadius = 25;
  const numLines = 6;
  const lineRadius = mediumCircleRadius;

  drawLines(ctx);
  drawTrapezoids(ctx);
  drawCircles(ctx, bigCircleRadius, mediumCircleRadius, smallCircleRadius, numLines, lineRadius);
}

function drawLines(ctx) {
  const lineData = [
    { points: [160, -60, 205, -70, 205, 70, 160, 60], fillColor: 'white', strokeWidth: 3 },
    { points: [195, -70, 205, -70, 205, 70, 195, 70], fillColor: 'white', strokeWidth: 2 },
    { points: [135, -150, 145, -150, 205, -70, 195, -70], fillColor: 'white', strokeWidth: 2 },
    { points: [135, 150, 145, 150, 205, 70, 195, 70], fillColor: 'white', strokeWidth: 2 },
    { points: [105, -135, 135, -150, 195, -70, 160, -60], fillColor: 'black', strokeWidth: 3 },
    { points: [105, 135, 135, 150, 195, 70, 160, 60], fillColor: 'black', strokeWidth: 3 },
    { points: [-160, -60, -205, -70, -205, 70, -160, 60], fillColor: 'white', strokeWidth: 3 },
    { points: [-195, -70, -205, -70, -205, 70, -195, 70], fillColor: 'white', strokeWidth: 2 },
    { points: [-135, -150, -145, -150, -205, -70, -195, -70], fillColor: 'white', strokeWidth: 2 },
    { points: [-135, 150, -145, 150, -205, 70, -195, 70], fillColor: 'white', strokeWidth: 2 },
    { points: [-105, -135, -135, -150, -195, -70, -160, -60], fillColor: 'black', strokeWidth: 3 },
    { points: [-105, 135, -135, 150, -195, 70, -160, 60], fillColor: 'black', strokeWidth: 3 }
  ];

  lineData.forEach(({ points, fillColor, strokeWidth }) => {
    ctx.beginPath();
    ctx.moveTo(points[0], points[1]);
    for (let i = 2; i < points.length; i += 2) {
      ctx.lineTo(points[i], points[i + 1]);
    }
    ctx.closePath();
    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.strokeStyle = '#303030';
    ctx.lineWidth = strokeWidth;
    ctx.stroke();
  });
}

function drawTrapezoids(ctx) {
  drawTrapezoid(ctx, 125, 0, 60, 60, 60, 60, true);
  drawTrapezoid(ctx, -125, 0, 60, 60, 60, 60, false);
}

function drawTrapezoid(ctx, x, y, width, height, topWidth, bottomWidth, isFirst) {
  ctx.beginPath();

  if (isFirst) {
    ctx.moveTo(x - width, y - height);
    ctx.lineTo(x + topWidth, y - height / 2);
    ctx.lineTo(x + bottomWidth, y + height / 2);
    ctx.lineTo(x - width, y + height);
  } else {
    ctx.moveTo(x - width, y - height / 2);
    ctx.lineTo(x + topWidth, y - height);
    ctx.lineTo(x + bottomWidth, y + height);
    ctx.lineTo(x - width, y + height / 2);
  }

  ctx.closePath();
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.strokeStyle = '#303030';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function drawCircles(ctx, big, medium, small, lines, radius) {
  // БОльший круг
  ctx.beginPath();
  ctx.arc(0, 0, big, 0, 2 * Math.PI);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.strokeStyle = '#303030';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Средний круг
  ctx.beginPath();
  ctx.arc(0, 0, medium, 0, 2 * Math.PI);
  ctx.fillStyle = 'black';
  ctx.fill();

  // Линии
  for (let i = 0; i < lines; i++) {
    const angle = (i * 2 * Math.PI) / lines;
    const x = radius * Math.cos(angle);
    const y = radius * Math.sin(angle);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(x, y);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 5;
    ctx.stroke();
  }

  // Внутренний
  ctx.beginPath();
  ctx.arc(0, 0, small, 0, 2 * Math.PI);
  ctx.fillStyle = 'black';
  ctx.fill();
  ctx.strokeStyle = 'white';
  ctx.lineWidth = 5;
  ctx.stroke();

  // Полоска
  ctx.beginPath();
  ctx.moveTo(-42, -80);
  ctx.lineTo(0, -80);
  ctx.lineTo(42, -80);
  ctx.strokeStyle = '#303030';
  ctx.lineWidth = 2;
  ctx.stroke();
}