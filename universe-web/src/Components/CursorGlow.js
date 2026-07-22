import { useEffect, useRef } from 'react';


export default function CursorGlow() {
  const glowRef = useRef(null);

  useEffect(() => {
    function handleMouseMove(e) {
      if (!glowRef.current) return;
      glowRef.current.style.left = `${e.clientX}px`;
      glowRef.current.style.top = `${e.clientY}px`;
      glowRef.current.style.opacity = '1';
    }
    function handleMouseLeave() {
      if (glowRef.current) glowRef.current.style.opacity = '0';
    }

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <div
      ref={glowRef}
      style={{
        position: 'fixed',
        pointerEvents: 'none',
        zIndex: 0,
        width: '520px',
        height: '520px',
        borderRadius: '50%',
        transform: 'translate(-50%, -50%)',
        background: 'radial-gradient(circle, rgba(99,120,255,0.10) 0%, rgba(6,182,212,0.06) 40%, transparent 70%)',
        opacity: 0,
        transition: 'opacity 0.3s ease',
      }}
    />
  );
}