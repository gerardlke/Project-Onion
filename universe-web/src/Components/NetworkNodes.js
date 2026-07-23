import { useState, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Billboard, Text } from '@react-three/drei';
import * as THREE from 'three';


const LABEL_SHOW_DISTANCE = 8;
const LABEL_HIDE_DISTANCE = 12;


export default function NetworkNode({
  position,
  color,
  radius = 0.4,
  data,
  activeNode,
  setActiveNode,
}) {
  const [hovered, setHover] = useState(false);
  const isOpen = activeNode?.id === data.id;

  const coreRef = useRef();
  const glowRef = useRef();
  const coronaRef = useRef();
  const lightRef = useRef();
  const labelRef = useRef();

  // Persistent lerp targets
  const currentColor = useRef(new THREE.Color(color));
  const currentEmissive = useRef(new THREE.Color(color));
  const currentGlowOpacity = useRef(0.18);
  const currentCoronaOpacity = useRef(0.06);
  const currentLightIntensity = useRef(1.8);
  const currentLabelOpacity = useRef(0);

  const phaseOffset = useRef(
    (typeof data.id === 'number' ? data.id : (data.id?.charCodeAt?.(0) ?? 0)) * 0.37
  );

  const baseColor = new THREE.Color(color);
  const hoverColor = new THREE.Color('#ffffff');
  const activeColor = new THREE.Color('#facc15');
  const glowColor = baseColor.clone().lerp(new THREE.Color('#ffffff'), 0.35);

  const { camera } = useThree();

  useFrame(({ clock }, delta) => {
    const t = clock.getElapsedTime() + phaseOffset.current;
    const LERP = 1 - Math.pow(0.01, delta * 4.5);

    // Resolve target states
    const targetColor = isOpen ? activeColor : hovered ? hoverColor : baseColor;
    const targetEmissive = targetColor;
    const targetGlowOpacity = isOpen ? 0.55 : hovered ? 0.38 : 0.18 + Math.sin(t * 0.9 + 1.1) * 0.09;
    const targetCoronaOpacity = isOpen ? 0.22 : hovered ? 0.14 : 0.06 + Math.sin(t * 0.55 + 2.3) * 0.04;
    const targetCoreEmissive = isOpen ? 1.6 : hovered ? 1.2 : 0.88 + Math.sin(t * 1.4) * 0.12;

    // Lerp colors channel by channel
    currentColor.current.lerp(targetColor, LERP);
    currentEmissive.current.lerp(targetEmissive, LERP);

    // Apply to materials
    if (coreRef.current) {
      coreRef.current.color.copy(currentColor.current);
      coreRef.current.emissive.copy(currentEmissive.current);
      currentLightIntensity.current += (targetCoreEmissive - currentLightIntensity.current) * LERP;
      coreRef.current.emissiveIntensity = currentLightIntensity.current;
    }
    if (glowRef.current) {
      glowRef.current.color.copy(glowColor.clone().lerp(currentColor.current, 0.4));
      currentGlowOpacity.current += (targetGlowOpacity - currentGlowOpacity.current) * LERP;
      glowRef.current.opacity = currentGlowOpacity.current;
    }
    if (coronaRef.current) {
      coronaRef.current.color.copy(glowColor.clone().lerp(currentColor.current, 0.25));
      currentCoronaOpacity.current += (targetCoronaOpacity - currentCoronaOpacity.current) * LERP;
      coronaRef.current.opacity = currentCoronaOpacity.current;
    }
    if (lightRef.current) {
      lightRef.current.intensity = currentLightIntensity.current * (isOpen ? 3.5 : hovered ? 2.2 : 1.0);
    }

    if (labelRef.current) {
      const worldPos = new THREE.Vector3(...position);
      const dist = camera.position.distanceTo(worldPos);
      const distTarget = 1 - THREE.MathUtils.clamp(
        (dist - LABEL_SHOW_DISTANCE) / (LABEL_HIDE_DISTANCE - LABEL_SHOW_DISTANCE),
        0, 1
      );
      const targetLabelOpacity = isOpen ? 1 : hovered ? 0.85 : distTarget;
      currentLabelOpacity.current += (targetLabelOpacity - currentLabelOpacity.current) * LERP;
      labelRef.current.fillOpacity = currentLabelOpacity.current;
    }

  });

  return (
    <group
      position={position}
      onClick={(e) => { e.stopPropagation(); setActiveNode(isOpen ? null : data); }}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); }}
      onPointerOut={() => setHover(false)}
    >
      <pointLight ref={lightRef} color={color} intensity={1.8} distance={radius * 14} decay={2} />

      {/* Corona */}
      <mesh>
        <sphereGeometry args={[radius * 2.8, 16, 16]} />
        <meshStandardMaterial 
        ref={coronaRef} 
        color={glowColor} 
        transparent 
        opacity={0.06} 
        depthWrite={false} 
        side={THREE.BackSide} />
      </mesh>

      {/* Glow halo */}
      <mesh>
        <sphereGeometry args={[radius * 1.7, 20, 20]} />
        <meshStandardMaterial 
        ref={glowRef} 
        color={glowColor} 
        transparent 
        opacity={0.18} 
        depthWrite={false} 
        side={THREE.BackSide} />
      </mesh>

      {/* Core */}
      <mesh>
        <sphereGeometry args={[radius, 32, 32]} />
        <meshStandardMaterial
          ref={coreRef}
          color={color}
          emissive={color}
          emissiveIntensity={0.9}
          roughness={0.15}
          metalness={0.1}
        />
      </mesh>

      <Billboard position={[0, radius * 2.2 + 0.15, 0]}>
        <Text
          ref={labelRef}
          fontSize={0.14}
          color="white"
          fillOpacity={0}
          anchorX="center"
          anchorY="bottom"
          font={undefined}
          outlineWidth={0.002}
          outlineColor="#ffffff"
          outlineOpacity={0.3}
          maxWidth={3}
          textAlign="center"
        >
          {data.label}
        </Text>
      </Billboard>
    </group>
  );
}