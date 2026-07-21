// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import { useRef, useState, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';

const FADE_SPEED = 6;
const DISTANCE_HIDE = 18;
const DISTANCE_SHOW = 12;
const ROTATION_FADE_DELAY = 80;

export default function NetworkEdge({
  edge,
  fromPos,
  toPos,
  fromColor,
  toColor,
  isActive,
  onClickEdge,
}) {
  const [hovered, setHovered] = useState(false);

  // Material refs for direct mutation in useFrame
  const tubeARef = useRef();
  const tubeBRef = useRef();
  const flowRef = useRef();
  const hitRef = useRef();

  const currentOpacityRef = useRef(0);
  const lastCameraPosRef = useRef(new THREE.Vector3());
  const stillSinceRef = useRef(0);
  const flowOffsetRef = useRef(0);

  const { camera } = useThree();

  const from = useMemo(() => new THREE.Vector3(...fromPos), [fromPos]);
  const to = useMemo(() => new THREE.Vector3(...toPos), [toPos]);

  // Full-length curve
  const fullCurve = useMemo(() => new THREE.LineCurve3(from, to), [from, to]);

  const mid = useMemo(() => from.clone().lerp(to, 0.5), [from, to]);
  const curveA = useMemo(() => new THREE.LineCurve3(from, mid), [from, mid]);
  const curveB = useMemo(() => new THREE.LineCurve3(mid, to), [mid, to]);

  const midpoint = useMemo(() => from.clone().lerp(to, 0.5), [from, to]);

  // Flow texture
  const flowTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 16;
    const ctx = canvas.getContext('2d');
    // Dark background
    ctx.fillStyle = 'rgba(0,0,0,0)';
    ctx.fillRect(0, 0, 256, 16);
    // Bright moving dots
    for (let i = 0; i < 5; i++) {
      const x = (i / 5) * 256 + 12;
      const grad = ctx.createRadialGradient(x, 8, 0, x, 8, 10);
      grad.addColorStop(0, 'rgba(255,255,255,0.95)');
      grad.addColorStop(0.4, 'rgba(255,255,255,0.4)');
      grad.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(x - 10, 0, 20, 16);
    }
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = THREE.RepeatWrapping;
    tex.repeat.set(3, 1);
    return tex;
  }, []);

  const srcColor = useMemo(() => new THREE.Color(fromColor ?? '#4f46e5'), [fromColor]);
  const tgtColor = useMemo(() => new THREE.Color(toColor ?? '#06b6d4'), [toColor]);
  const activeColor = useMemo(() => new THREE.Color('#facc15'), []);
  const hoverColor = useMemo(() => new THREE.Color('#ffffff'), []);

  const weightedOpacity = Math.max(0.12, Math.min(0.7, edge.weight ?? 0.4));

  useFrame((_, delta) => {
    // Camera movement detection
    const moved = camera.position.distanceTo(lastCameraPosRef.current) > 0.001;
    if (moved) {
      stillSinceRef.current = 0;
      lastCameraPosRef.current.copy(camera.position);
    } else {
      stillSinceRef.current += delta * 1000;
    }
    const cameraMoving = stillSinceRef.current < ROTATION_FADE_DELAY;

    // Distance fade
    const dist = camera.position.distanceTo(midpoint);
    const distFactor = 1 - THREE.MathUtils.clamp(
      (dist - DISTANCE_SHOW) / (DISTANCE_HIDE - DISTANCE_SHOW), 0, 1
    );

    // Resolve target opacity
    let targetOpacity;
    if (isActive) targetOpacity = 1;
    else if (cameraMoving) targetOpacity = 0;
    else if (hovered) targetOpacity = 0.75;
    else targetOpacity = weightedOpacity * distFactor;

    const LERP = 1 - Math.pow(0.01, delta * FADE_SPEED);
    currentOpacityRef.current += (targetOpacity - currentOpacityRef.current) * LERP;
    const op = currentOpacityRef.current;

    // Resolve tube colors — lerp toward active/hover tint
    const blendStrength = isActive ? 1 : hovered ? 0.6 : 0;
    const targetA = srcColor.clone().lerp(isActive ? activeColor : hoverColor, blendStrength);
    const targetB = tgtColor.clone().lerp(isActive ? activeColor : hoverColor, blendStrength);

    if (tubeARef.current) {
      tubeARef.current.color.lerp(targetA, LERP);
      tubeARef.current.emissive.lerp(targetA, LERP);
      tubeARef.current.emissiveIntensity = isActive ? 0.9 : hovered ? 0.5 : 0.2;
      tubeARef.current.opacity = op;
    }
    if (tubeBRef.current) {
      tubeBRef.current.color.lerp(targetB, LERP);
      tubeBRef.current.emissive.lerp(targetB, LERP);
      tubeBRef.current.emissiveIntensity = isActive ? 0.9 : hovered ? 0.5 : 0.2;
      tubeBRef.current.opacity = op;
    }

    // Animate flow texture offset — faster when active/hovered
    const flowSpeed = isActive ? 0.9 : hovered ? 0.55 : 0.25;
    flowOffsetRef.current += delta * flowSpeed;
    if (flowRef.current?.map) {
      flowRef.current.map.offset.x = -flowOffsetRef.current;
      flowRef.current.opacity = op * (isActive ? 0.85 : hovered ? 0.55 : 0.28);
    }
  });

  return (
    <group>
      {/* Source-colored half tube */}
      <mesh>
        <tubeGeometry args={[curveA, 6, 0.03, 6, false]} />
        <meshStandardMaterial
          ref={tubeARef}
          color={fromColor}
          emissive={fromColor}
          emissiveIntensity={0.2}
          transparent
          opacity={0}
          depthWrite={false}
        />
      </mesh>

      {/* Target-colored half tube */}
      <mesh>
        <tubeGeometry args={[curveB, 6, 0.03, 6, false]} />
        <meshStandardMaterial
          ref={tubeBRef}
          color={toColor}
          emissive={toColor}
          emissiveIntensity={0.2}
          transparent
          opacity={0}
          depthWrite={false}
        />
      </mesh>

      {/* Flow overlay — animated bright dots scrolling along full length */}
      <mesh>
        <tubeGeometry args={[fullCurve, 12, 0.018, 6, false]} />
        <meshStandardMaterial
          ref={flowRef}
          map={flowTexture}
          transparent
          opacity={0}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Invisible wide hit tube for hover/click */}
      <mesh
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true); }}
        onPointerOut={() => setHovered(false)}
        onClick={(e) => { e.stopPropagation(); onClickEdge(); }}
      >
        <tubeGeometry args={[fullCurve, 8, 0.18, 6, false]} />
        <meshStandardMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
    </group>
  );
}