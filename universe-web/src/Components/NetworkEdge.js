import { useRef, useState } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';

const FADE_SPEED = 6;           // higher = faster fade in/out
const DISTANCE_HIDE = 18;       // camera distance at which edges fully vanish
const DISTANCE_SHOW = 12;       // camera distance at which edges are fully visible
const ROTATION_FADE_DELAY = 80; // ms of camera stillness before fading back in

export default function NetworkEdge({ edge, fromPos, toPos, isActive, onClickEdge }) {
  const [hovered, setHovered] = useState(false);
  const visibleRef = useRef();
  const targetOpacityRef = useRef(0);
  const currentOpacityRef = useRef(0);
  const lastCameraPosRef = useRef(new THREE.Vector3());
  const stillSinceRef = useRef(0);

  const { camera } = useThree();

  const from = new THREE.Vector3(...fromPos);
  const to = new THREE.Vector3(...toPos);
  const curve = new THREE.LineCurve3(from, to);
  const midpoint = new THREE.Vector3().lerpVectors(from, to, 0.5);

  // Base opacity from weight, floored so faint edges are still visible
  const weightedOpacity = Math.max(0.12, Math.min(0.7, edge.weight ?? 0.4));

  useFrame((_, delta) => {
    if (!visibleRef.current) return;

    // Detect camera movement
    const camPos = camera.position;
    const moved = camPos.distanceTo(lastCameraPosRef.current) > 0.001;

    if (moved) {
      stillSinceRef.current = 0;
      lastCameraPosRef.current.copy(camPos);
    } else {
      stillSinceRef.current += delta * 1000;
    }

    const cameraIsMoving = stillSinceRef.current < ROTATION_FADE_DELAY;

    // Distance from camera to edge midpoint
    const dist = camera.position.distanceTo(midpoint);
    const distanceFactor = 1 - THREE.MathUtils.clamp(
      (dist - DISTANCE_SHOW) / (DISTANCE_HIDE - DISTANCE_SHOW),
      0, 1
    );

    // Resolve what opacity this edge should be targeting
    let target;
    if (isActive) {
      target = 1;
    } else if (cameraIsMoving) {
      target = 0;
    } else if (hovered) {
      target = 0.85;
    } else {
      target = weightedOpacity * distanceFactor;
    }

    targetOpacityRef.current = target;

    currentOpacityRef.current = THREE.MathUtils.lerp(
      currentOpacityRef.current,
      targetOpacityRef.current,
      delta * FADE_SPEED
    );

    visibleRef.current.opacity = currentOpacityRef.current;
  });

  return (
    <group>
      <mesh>
        <tubeGeometry args={[curve, 8, 0.04, 6, false]} />
        <meshStandardMaterial
          ref={visibleRef}
          color={isActive ? '#facc15' : hovered ? '#fde68a' : 'white'}
          transparent
          opacity={0}
          emissive={isActive ? '#facc15' : hovered ? '#fde68a' : '#000000'}
          emissiveIntensity={isActive ? 0.7 : hovered ? 0.3 : 0}
          depthWrite={false}
        />
      </mesh>

      <mesh
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true); }}
        onPointerOut={() => setHovered(false)}
        onClick={(e) => { e.stopPropagation(); onClickEdge(); }}
      >
        <tubeGeometry args={[curve, 8, 0.18, 6, false]} />
        <meshStandardMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
    </group>
  );
}