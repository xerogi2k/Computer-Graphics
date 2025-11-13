const mazeSize = 16;
const blockSize = 10;
const wallHeight = 10;

let camera, scene, renderer;
let controls = { forward: false, backward: false, left: false, right: false };
let maze = [];
let walls = [];

init();
animate();

function init() {
  // Создание сцены и камеры
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 1000);
  camera.position.set(blockSize * 1.5, wallHeight / 2, blockSize * 1.5);

  // Освещение, закреплённое на камере
  const light = new THREE.PointLight(0xffffff, 1, 100);
  camera.add(light);
  scene.add(camera);

  // Рендерер
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  generateMaze();

  // Обработчики клавиш
  document.addEventListener('keydown', onKeyDown);
  document.addEventListener('keyup', onKeyUp);
  window.addEventListener('resize', onWindowResize);
}

function generateMaze() {
  // Простой лабиринт (16x16): 0 - пусто, 1 - стена
  for (let z = 0; z < mazeSize; z++) {
    maze[z] = [];
    for (let x = 0; x < mazeSize; x++) {
      // Граница всегда стена
      maze[z][x] = (x === 0 || x === mazeSize - 1 || z === 0 || z === mazeSize - 1) ? 1 : Math.random() < 0.3 ? 1 : 0;
      if (maze[z][x] === 1) {
        const wall = new THREE.Mesh(
          new THREE.BoxGeometry(blockSize, wallHeight, blockSize),
          new THREE.MeshStandardMaterial({ color: 0x5555ff })
        );
        wall.position.set(x * blockSize, wallHeight / 2, z * blockSize);
        scene.add(wall);
        walls.push(wall);
      }
    }
  }

  // Пол и потолок
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(mazeSize * blockSize, mazeSize * blockSize),
    new THREE.MeshStandardMaterial({ color: 0x00aa00 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = 0;
  scene.add(floor);

  const ceiling = new THREE.Mesh(
    new THREE.PlaneGeometry(mazeSize * blockSize, mazeSize * blockSize),
    new THREE.MeshStandardMaterial({ color: 0xaa0000 })
  );
  ceiling.rotation.x = Math.PI / 2;
  ceiling.position.y = wallHeight;
  scene.add(ceiling);
}

function onKeyDown(event) {
  switch (event.key) {
    case 'w': controls.forward = true; break;
    case 's': controls.backward = true; break;
    case 'a': controls.left = true; break;
    case 'd': controls.right = true; break;
    case 'ArrowLeft': camera.rotation.y += 0.1; break;
    case 'ArrowRight': camera.rotation.y -= 0.1; break;
  }
}

function onKeyUp(event) {
  switch (event.key) {
    case 'w': controls.forward = false; break;
    case 's': controls.backward = false; break;
    case 'a': controls.left = false; break;
    case 'd': controls.right = false; break;
  }
}

function animate() {
  requestAnimationFrame(animate);

  const speed = 1.5;
  const direction = new THREE.Vector3();
  camera.getWorldDirection(direction);
  direction.y = 0;
  direction.normalize();

  let moveX = 0, moveZ = 0;

  if (controls.forward) {
    moveX += direction.x;
    moveZ += direction.z;
  }
  if (controls.backward) {
    moveX -= direction.x;
    moveZ -= direction.z;
  }
  if (controls.left) {
    moveX += direction.z;
    moveZ -= direction.x;
  }
  if (controls.right) {
    moveX -= direction.z;
    moveZ += direction.x;
  }

  const newPos = camera.position.clone().add(new THREE.Vector3(moveX, 0, moveZ).normalize().multiplyScalar(speed));

  // Проверка столкновений
  if (!checkCollision(newPos)) {
    camera.position.copy(newPos);
  }

  renderer.render(scene, camera);
}

function checkCollision(pos) {
  for (const wall of walls) {
    const dist = wall.position.distanceTo(pos);
    if (dist < blockSize * 0.75) return true;
  }
  return false;
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}