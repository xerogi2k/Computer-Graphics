    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    function putPixel(x, y, color) {
      if (x >= 0 && x < width && y >= 0 && y < height) {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, 1, 1);
      }
    }

    // Коэн-Сазерленд для отсечения
    const INSIDE = 0, LEFT = 1, RIGHT = 2, BOTTOM = 4, TOP = 8;

    function computeOutCode(x, y) {
      let code = INSIDE;
      if (x < 0) code |= LEFT;
      else if (x >= width) code |= RIGHT;
      if (y < 0) code |= TOP;
      else if (y >= height) code |= BOTTOM;
      return code;
    }

    function cohenSutherlandClip(x0, y0, x1, y1) {
      let outcode0 = computeOutCode(x0, y0);
      let outcode1 = computeOutCode(x1, y1);
      let accept = false;

      while (true) {
        if (!(outcode0 | outcode1)) {
          accept = true;
          break;
        } else if (outcode0 & outcode1) {
          break;
        } else {
          let x, y;
          const outcodeOut = outcode0 ? outcode0 : outcode1;

          if (outcodeOut & TOP) {
            x = x0 + (x1 - x0) * (0 - y0) / (y1 - y0);
            y = 0;
          } else if (outcodeOut & BOTTOM) {
            x = x0 + (x1 - x0) * (height - 1 - y0) / (y1 - y0);
            y = height - 1;
          } else if (outcodeOut & RIGHT) {
            y = y0 + (y1 - y0) * (width - 1 - x0) / (x1 - x0);
            x = width - 1;
          } else if (outcodeOut & LEFT) {
            y = y0 + (y1 - y0) * (0 - x0) / (x1 - x0);
            x = 0;
          }

          if (outcodeOut === outcode0) {
            x0 = x;
            y0 = y;
            outcode0 = computeOutCode(x0, y0);
          } else {
            x1 = x;
            y1 = y;
            outcode1 = computeOutCode(x1, y1);
          }
        }
      }
      if (accept) return [Math.round(x0), Math.round(y0), Math.round(x1), Math.round(y1)];
      else return null;
    }

    function bresenham(x0, y0, x1, y1, color) {
      const dx = Math.abs(x1 - x0);
      const dy = Math.abs(y1 - y0);
      const sx = x0 < x1 ? 1 : -1;
      const sy = y0 < y1 ? 1 : -1;
      let err = dx - dy;

      while (true) {
        putPixel(x0, y0, color);
        if (x0 === x1 && y0 === y1) break;
        const e2 = 2 * err;
        if (e2 > -dy) {
          err -= dy;
          x0 += sx;
        }
        if (e2 < dx) {
          err += dx;
          y0 += sy;
        }
      }
    }

    function drawLine() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      let x0 = parseInt(document.getElementById("x1").value);
      let y0 = parseInt(document.getElementById("y1").value);
      let x1 = parseInt(document.getElementById("x2").value);
      let y1 = parseInt(document.getElementById("y2").value);
      const color = document.getElementById("color").value;

      const clipped = cohenSutherlandClip(x0, y0, x1, y1);
      if (clipped) {
        bresenham(clipped[0], clipped[1], clipped[2], clipped[3], color);
      } else {
        alert("Линия полностью вне области экрана.");
      }
    }