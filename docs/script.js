/* =========================================================
   AeroLaunch — projectile motion engine
   Ported from main.py (Euler + RK4 integrators, drag,
   barometric density, optimal-angle search).
   ========================================================= */

// ---- Physical constants (match main.py) ----
const G = 9.81;          // gravity, m/s^2
const RHO = 1.225;       // sea-level air density, kg/m^3
const MM = 0.029;        // molar mass of air, kg/mol
const R_GAS = 8.314;     // universal gas constant
const TEMP = 288.15;     // standard temperature, K

const CD = 0.47;         // drag coefficient (sphere)
const RADIUS = 0.05;     // m
const MASS = 0.5;        // kg
const AREA = Math.PI * RADIUS * RADIUS;

// Simulation timestep. main.py uses 0.001 for research-grade
// precision; the browser uses a larger step so the console
// stays responsive, with a fine cap on iteration count.
const DT = 0.004;
const MAX_STEPS = 20000;

function computeAcceleration(vx, vy, wind, height, drag) {
  const relVx = vx + wind;
  const relVy = vy;
  const relV = Math.sqrt(relVx * relVx + relVy * relVy);

  const airDensity = RHO * Math.exp((-MM * G * height) / (R_GAS * TEMP));
  const dragFactor = drag ? (airDensity * CD * AREA) / (2 * MASS) : 0;

  const ax = -dragFactor * relV * relVx;
  const ay = -G - dragFactor * relV * relVy;
  return [ax, ay];
}

function simulateEuler(v0, angleDeg, wind, drag) {
  const angle = (angleDeg * Math.PI) / 180;
  let vx = v0 * Math.cos(angle);
  let vy = v0 * Math.sin(angle);
  let x = 0, y = 0;

  const xs = [x], ys = [y];

  while (y >= 0) {
    const [ax, ay] = computeAcceleration(vx, vy, wind, y, drag);
    vx += ax * DT;
    vy += ay * DT;
    x += vx * DT;
    y += vy * DT;
    xs.push(x); ys.push(y);
    if (xs.length > MAX_STEPS || x < -10) break;
  }
  return { xs, ys, range: x };
}

function simulateRK4(v0, angleDeg, wind, drag) {
  const angle = (angleDeg * Math.PI) / 180;
  let x = 0, y = 0;
  let vx = v0 * Math.cos(angle);
  let vy = v0 * Math.sin(angle);

  const xs = [x], ys = [y];

  while (y >= 0) {
    const [k1vx, k1vy] = computeAcceleration(vx, vy, wind, y, drag);

    const vx2 = vx + (DT / 2) * k1vx;
    const vy2 = vy + (DT / 2) * k1vy;
    const [k2vx, k2vy] = computeAcceleration(vx2, vy2, wind, y + (DT / 2) * vy, drag);

    const vx3 = vx + (DT / 2) * k2vx;
    const vy3 = vy + (DT / 2) * k2vy;
    const [k3vx, k3vy] = computeAcceleration(vx3, vy3, wind, y + (DT / 2) * vy2, drag);

    const vx4 = vx + DT * k3vx;
    const vy4 = vy + DT * k3vy;
    const [k4vx, k4vy] = computeAcceleration(vx4, vy4, wind, y + DT * vy3, drag);

    x += (DT / 6) * (vx + 2 * vx2 + 2 * vx3 + vx4);
    y += (DT / 6) * (vy + 2 * vy2 + 2 * vy3 + vy4);

    vx += (DT / 6) * (k1vx + 2 * k2vx + 2 * k3vx + k4vx);
    vy += (DT / 6) * (k1vy + 2 * k2vy + 2 * k3vy + k4vy);

    xs.push(x); ys.push(y);
    if (xs.length > MAX_STEPS || x < -10) break;
  }
  return { xs, ys, range: x };
}

function simulate(method, v0, angleDeg, wind, drag) {
  return method === "euler"
    ? simulateEuler(v0, angleDeg, wind, drag)
    : simulateRK4(v0, angleDeg, wind, drag);
}

// Golden-section search for the angle in [1, 89] that
// maximizes range — a dependency-free stand-in for
// scipy.optimize.minimize_scalar(method='bounded').
function findOptimalAngle(method, v0, wind, drag) {
  const phi = (Math.sqrt(5) - 1) / 2;
  let lo = 1, hi = 89;
  let a = hi - phi * (hi - lo);
  let b = lo + phi * (hi - lo);
  let fa = simulate(method, v0, a, wind, drag).range;
  let fb = simulate(method, v0, b, wind, drag).range;

  for (let i = 0; i < 22; i++) {
    if (fa < fb) {
      lo = a; a = b; fa = fb;
      b = lo + phi * (hi - lo);
      fb = simulate(method, v0, b, wind, drag).range;
    } else {
      hi = b; b = a; fb = fa;
      a = hi - phi * (hi - lo);
      fa = simulate(method, v0, a, wind, drag).range;
    }
  }

  const angle = (lo + hi) / 2;
  const result = simulate(method, v0, angle, wind, drag);
  return { angle, ...result };
}

/* =========================================================
   Canvas rendering — a ballistics-scope style plot with a
   tracer reveal animation.
   ========================================================= */

const canvas = document.getElementById("trajectoryCanvas");
const ctx = canvas.getContext("2d");
const scopeStatus = document.getElementById("scopeStatus");

function resizeCanvas() {
  const rect = canvas.parentElement.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  canvas.style.width = rect.width + "px";
  canvas.style.height = rect.height + "px";
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function niceStep(maxVal, targetTicks) {
  const raw = maxVal / targetTicks;
  const mag = Math.pow(10, Math.floor(Math.log10(raw || 1)));
  const norm = raw / mag;
  let step;
  if (norm < 1.5) step = 1;
  else if (norm < 3.5) step = 2;
  else if (norm < 7.5) step = 5;
  else step = 10;
  return step * mag;
}

function drawScene(traces, progress) {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  ctx.clearRect(0, 0, w, h);

  const pad = { left: 46, right: 18, top: 18, bottom: 34 };
  const plotW = w - pad.left - pad.right;
  const plotH = h - pad.top - pad.bottom;

  let maxX = 10, maxY = 5;
  traces.forEach(t => {
    for (let i = 0; i < t.xs.length; i++) {
      if (t.xs[i] > maxX) maxX = t.xs[i];
      if (t.ys[i] > maxY) maxY = t.ys[i];
    }
  });
  maxX *= 1.08;
  maxY *= 1.25;

  const sx = v => pad.left + (v / maxX) * plotW;
  const sy = v => pad.top + plotH - (v / maxY) * plotH;

  // grid
  ctx.strokeStyle = getCss("--grid-line");
  ctx.lineWidth = 1;
  ctx.font = "10px 'JetBrains Mono', monospace";
  ctx.fillStyle = getCss("--ink-dim");

  const xStep = niceStep(maxX, 6);
  const yStep = niceStep(maxY, 4);

  ctx.beginPath();
  for (let v = 0; v <= maxX; v += xStep) {
    const px = Math.round(sx(v)) + 0.5;
    ctx.moveTo(px, pad.top);
    ctx.lineTo(px, pad.top + plotH);
  }
  for (let v = 0; v <= maxY; v += yStep) {
    const py = Math.round(sy(v)) + 0.5;
    ctx.moveTo(pad.left, py);
    ctx.lineTo(pad.left + plotW, py);
  }
  ctx.stroke();

  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (let v = 0; v <= maxX; v += xStep) {
    ctx.fillText(Math.round(v), sx(v), pad.top + plotH + 8);
  }
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let v = 0; v <= maxY; v += yStep) {
    ctx.fillText(Math.round(v), pad.left - 8, sy(v));
  }

  // ground line
  ctx.strokeStyle = getCss("--ink-dim");
  ctx.beginPath();
  ctx.moveTo(pad.left, sy(0) + 0.5);
  ctx.lineTo(pad.left + plotW, sy(0) + 0.5);
  ctx.stroke();

  // trajectories, revealed up to `progress` (0..1)
  traces.forEach(t => {
    const n = t.xs.length;
    const upTo = Math.max(2, Math.floor(n * progress));

    ctx.beginPath();
    ctx.strokeStyle = t.color;
    ctx.lineWidth = t.width || 2;
    if (t.dashed) ctx.setLineDash([6, 5]); else ctx.setLineDash([]);

    for (let i = 0; i < upTo; i++) {
      const px = sx(t.xs[i]);
      const py = sy(Math.max(0, t.ys[i]));
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // tracer head
    if (upTo < n) {
      const hx = sx(t.xs[upTo - 1]);
      const hy = sy(Math.max(0, t.ys[upTo - 1]));
      ctx.beginPath();
      ctx.fillStyle = t.color;
      ctx.arc(hx, hy, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

function getCss(varName) {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
}

let animId = null;

function animateTraces(traces, duration = 900) {
  if (animId) cancelAnimationFrame(animId);
  const start = performance.now();
  scopeStatus.textContent = "TRACKING";
  scopeStatus.classList.add("live");

  function frame(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    drawScene(traces, eased);
    if (t < 1) {
      animId = requestAnimationFrame(frame);
    } else {
      scopeStatus.textContent = "IMPACT";
      setTimeout(() => {
        scopeStatus.textContent = "STANDBY";
        scopeStatus.classList.remove("live");
      }, 900);
    }
  }
  animId = requestAnimationFrame(frame);
}

/* =========================================================
   UI wiring
   ========================================================= */

const el = id => document.getElementById(id);

const velocityRange = el("velocityRange"), velocityNum = el("velocity");
const angleRange = el("angleRange"), angleNum = el("angle");
const windRange = el("windRange"), windNum = el("wind");
const launchBtn = el("launchBtn");
const methodButtons = document.querySelectorAll(".toggle-btn");

let currentMethod = "rk4";

function linkPair(rangeEl, numEl) {
  rangeEl.addEventListener("input", () => { numEl.value = rangeEl.value; });
  numEl.addEventListener("input", () => {
    const clamped = Math.min(Number(numEl.max), Math.max(Number(numEl.min), Number(numEl.value || 0)));
    rangeEl.value = clamped;
  });
}
linkPair(velocityRange, velocityNum);
linkPair(angleRange, angleNum);
linkPair(windRange, windNum);

methodButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    methodButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentMethod = btn.dataset.method;
  });
});

function animateDigits(elDigits, target, duration = 700) {
  const start = performance.now();
  const from = 0;
  function step(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    const val = from + (target - from) * eased;
    elDigits.textContent = val.toFixed(1);
    if (t < 1) requestAnimationFrame(step);
    else elDigits.textContent = target.toFixed(1);
  }
  requestAnimationFrame(step);
}

function setReadout(key, value, angleText) {
  const readout = document.querySelector(`.readout[data-key="${key}"]`);
  animateDigits(readout.querySelector(".digits"), value);
  const angleEl = readout.querySelector(".readout-angle");
  if (angleEl) angleEl.textContent = angleText ? `(${angleText}°)` : "";
}

function runSimulation() {
  const v0 = Number(velocityNum.value);
  const angle = Number(angleNum.value);
  const wind = Number(windNum.value);
  const method = currentMethod;

  const userDrag = simulate(method, v0, angle, wind, true);
  const userVacuum = simulate(method, v0, angle, wind, false);
  const optDrag = findOptimalAngle(method, v0, wind, true);
  const optVacuum = findOptimalAngle(method, v0, wind, false);

  setReadout("userDrag", userDrag.range);
  setReadout("userVacuum", userVacuum.range);
  setReadout("optDrag", optDrag.range, optDrag.angle.toFixed(1));
  setReadout("optVacuum", optVacuum.range, optVacuum.angle.toFixed(1));

  const dragCost = userVacuum.range > 0
    ? (1 - userDrag.range / userVacuum.range) * 100
    : 0;
  el("deltaPct").textContent = `${dragCost.toFixed(1)}%`;

  const traces = [
    { xs: userDrag.xs, ys: userDrag.ys, color: getCss("--tracer-drag"), width: 2.5 },
    { xs: userVacuum.xs, ys: userVacuum.ys, color: getCss("--tracer-vacuum"), width: 2.5 },
    { xs: optDrag.xs, ys: optDrag.ys, color: getCss("--optimal-drag"), width: 1.6, dashed: true },
    { xs: optVacuum.xs, ys: optVacuum.ys, color: getCss("--optimal-vacuum"), width: 1.6, dashed: true },
  ];

  animateTraces(traces);
}

launchBtn.addEventListener("click", runSimulation);

window.addEventListener("resize", () => {
  resizeCanvas();
});

// Initial paint
resizeCanvas();
drawScene([{ xs: [0, 1], ys: [0, 0], color: getCss("--ink-dim"), width: 1 }], 1);
runSimulation();