import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Sphere, MeshDistortMaterial, Float, Environment, ContactShadows } from '@react-three/drei'
import { useRef } from 'react'
import * as THREE from 'three'

function OrbMesh({ valence, arousal, emotion }){
  const ref = useRef()
  useFrame((state)=>{
    if(!ref.current) return
    const t = state.clock.elapsedTime
    // arousal -> speed & distortion, valence -> color hue
    ref.current.rotation.y = t * (0.15 + arousal*0.6)
    ref.current.rotation.x = Math.sin(t*0.5)*0.2
  })
  // color mapping: valence -1 (blue) -> 0 (purple) -> +1 (warm gold)
  const hue = 0.65 - (valence+1)/2 * 0.55 // 0.65 blue -> 0.1 gold
  const color = new THREE.Color().setHSL(hue, 0.85, 0.58)
  const distort = 0.15 + arousal*0.45
  const speed = 1 + arousal*2

  return (
    <Float speed={1+arousal} rotationIntensity={0.3} floatIntensity={0.6}>
      <Sphere ref={ref} args={[1, 64, 64]} scale={1.15}>
        <MeshDistortMaterial color={color} distort={distort} speed={speed} roughness={0.2} metalness={0.15} emissive={color} emissiveIntensity={0.25} />
      </Sphere>
    </Float>
  )
}

export default function EmotionOrb({ valence=0, arousal=0.4, primary='calm', size=220 }){
  return (
    <div style={{width:size, height:size}} className="rounded-full overflow-hidden relative">
      <Canvas camera={{position:[0,0,3], fov:45}} dpr={[1,2]} gl={{antialias:true, alpha:true}}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[3,3,2]} intensity={1.2} />
        <pointLight position={[-2, -1, 2]} intensity={0.8} color="#a78bfa" />
        <OrbMesh valence={valence} arousal={arousal} emotion={primary} />
        <Environment preset="city" />
        <ContactShadows position={[0,-1.2,0]} opacity={0.2} scale={4} blur={2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.6} />
      </Canvas>
      <div className="absolute inset-0 pointer-events-none rounded-full" style={{boxShadow:'inset 0 0 40px rgba(255,255,255,0.35), inset 0 0 80px rgba(168,85,247,0.15)'}} />
      <div className="absolute bottom-1 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur text-white text-[10px] px-2 py-0.5 rounded-full">
        {primary || 'neutral'} · v{valence.toFixed(2)} a{arousal.toFixed(2)}
      </div>
    </div>
  )
}
