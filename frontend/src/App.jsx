import { Routes, Route, Navigate, Link, useNavigate, useLocation } from 'react-router-dom'
import Companion from './pages/Companion'
import Journal from './pages/Journal'
import Settings from './pages/Settings'
import Login from './pages/Login'

function Nav(){
  const nav=useNavigate()
  const loc=useLocation()
  const logout=()=>{localStorage.removeItem('token'); nav('/login')}
  const token=localStorage.getItem('token')
  const isActive=(p)=> loc.pathname===p
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-2xl bg-black/60 border-b border-white/[0.08] px-4 md:px-6 py-3 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-3 group">
        <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-cyan-400 flex items-center justify-center shadow-[0_10px_30px_rgba(139,92,246,0.45)] group-hover:scale-[1.04] transition" style={{transform:'perspective(500px) rotateY(-10deg)'}}>
          <span className="text-white text-lg">♫</span>
          <span className="absolute inset-0 rounded-xl bg-gradient-to-tr from-white/20 to-transparent" />
        </div>
        <div className="leading-tight">
          <div className="font-black tracking-tight text-white text-[15px] flex items-center gap-1.5">EMOTION 3D <span className="text-[10px] tracking-[0.2em] font-bold bg-white text-black px-1.5 py-0.5 rounded">MUSIC</span></div>
          <div className="text-[11px] tracking-wide text-white/50 -mt-0.5">valence · arousal · play</div>
        </div>
      </Link>
      <div className="flex items-center gap-1.5">
        {[
          ['/','Companion','◉'],
          ['/journal','Journal','✎'],
          ['/settings','Settings','◈'],
        ].map(([to,label,icon])=> (
          <Link key={to} to={to} className={`px-3.5 py-2 rounded-full text-xs font-semibold border backdrop-blur transition flex items-center gap-1.5 ${isActive(to) ? 'bg-white text-black border-white shadow-[0_8px_20px_rgba(255,255,255,0.25)]' : 'bg-white/[0.06] text-white/75 border-white/10 hover:bg-white/10 hover:text-white'}`}>
            <span>{icon}</span> {label}
          </Link>
        ))}
        <div className="w-px h-6 bg-white/10 mx-1 hidden sm:block" />
        {token ? <button onClick={logout} className="px-4 py-2 rounded-full bg-gradient-to-br from-white to-zinc-100 text-black text-xs font-black border border-white/20">Logout</button> : <Link to="/login" className="px-4 py-2 rounded-full bg-white text-black text-xs font-black">Login</Link>}
      </div>
    </nav>
  )
}
export default function App(){
  return (
    <div className="min-h-screen bg-[#06060a] text-white selection:bg-fuchsia-500/30 overflow-x-hidden">
      {/* ultra attractive animated background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-[#06060a]" />
        <div className="absolute inset-0 opacity-60" style={{background:'radial-gradient(800px 400px at 20% 10%, rgba(124,58,237,0.35), transparent 60%), radial-gradient(700px 500px at 90% 85%, rgba(236,72,153,0.28), transparent 60%), radial-gradient(600px 300px at 50% 40%, rgba(56,189,248,0.18), transparent 60%)'}} />
        {/* mesh grid */}
        <div className="absolute inset-0 opacity-[0.04]" style={{backgroundImage:'linear-gradient(white 1px, transparent 1px), linear-gradient(90deg, white 1px, transparent 1px)', backgroundSize:'40px 40px'}} />
        {/* floating orbs */}
        <div className="absolute top-[8%] left-[18%] w-[520px] h-[520px] bg-violet-600/30 blur-[90px] rounded-full animate-pulse" />
        <div className="absolute bottom-[12%] right-[8%] w-[620px] h-[620px] bg-fuchsia-600/22 blur-[100px] rounded-full" />
        <div className="absolute top-[45%] left-1/2 -translate-x-1/2 w-[900px] h-[420px] bg-cyan-500/12 blur-[80px] rounded-full" />
      </div>
      <Nav/>
      <Routes>
        <Route path="/" element={<Companion/>}/>
        <Route path="/journal" element={<Journal/>}/>
        <Route path="/settings" element={<Settings/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="*" element={<Navigate to="/"/>}/>
      </Routes>
      <footer className="text-center text-[11px] tracking-wide text-white/30 py-10">Crafted 3D glass · WebGL orb · SoundHelix streaming · Not a medical service</footer>
    </div>
  )
}
