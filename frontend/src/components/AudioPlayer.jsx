import { useEffect, useRef, useState } from 'react'

export default function AudioPlayer({ queue, currentIndex, setIndex, onEnded }){
  const audioRef = useRef(null)
  const canvasRef = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(0.9)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState("audio") // audio or youtube
  const track = queue[currentIndex]
  const animRef = useRef(0)

  const isYoutube = !!(track?.youtube_id || (track?.youtube_url && track.youtube_url.includes('youtube')))
  const youtubeId = track?.youtube_id || (track?.youtube_url ? track.youtube_url.split('v=')[1]?.split('&')[0] : null)

  // waveform
  useEffect(()=>{
    const canvas = canvasRef.current
    if(!canvas) return
    const ctx = canvas.getContext('2d')
    let w = canvas.width, h = canvas.height
    const draw = ()=>{
      ctx.clearRect(0,0,w,h)
      const bars = 32
      for(let i=0;i<bars;i++){
        const base = playing ? 8 + Math.random()*28 + Math.sin(Date.now()/180 + i)*6 : 4
        const bh = playing ? base : 4 + Math.random()*4
        const x = i*(w/bars) + 2
        const bw = w/bars - 4
        const y = (h - bh)/2
        const grad = ctx.createLinearGradient(0,0,0,h)
        grad.addColorStop(0, '#a78bfa'); grad.addColorStop(1, '#ec4899')
        ctx.fillStyle = grad
        ctx.fillRect(x, y, bw, bh)
      }
      animRef.current = requestAnimationFrame(draw)
    }
    draw()
    return ()=> cancelAnimationFrame(animRef.current)
  },[playing])

  // audio events
  useEffect(()=>{
    const a = audioRef.current
    if(!a || isYoutube) return
    const onTime = ()=> setProgress(a.currentTime)
    const onDur = ()=> { setDuration(a.duration || track?.duration_ms/1000 || 0); setLoading(false)}
    const onLoad = ()=> { setLoading(true); setError("")}
    const onCanPlay = ()=> { setLoading(false); setDuration(a.duration || 0) }
    const onErr = ()=> { setError("MP3 failed — switching to YouTube full song."); setMode("youtube"); setLoading(false); setPlaying(false)}
    const onEnd = ()=> { setPlaying(false); setProgress(0); onEnded?.() }
    const onPlay = ()=> setPlaying(true)
    const onPause = ()=> setPlaying(false)
    a.addEventListener('timeupdate', onTime); a.addEventListener('loadedmetadata', onDur)
    a.addEventListener('loadstart', onLoad); a.addEventListener('canplay', onCanPlay)
    a.addEventListener('error', onErr); a.addEventListener('ended', onEnd)
    a.addEventListener('play', onPlay); a.addEventListener('pause', onPause)
    return ()=>{
      a.removeEventListener('timeupdate', onTime); a.removeEventListener('loadedmetadata', onDur)
      a.removeEventListener('loadstart', onLoad); a.removeEventListener('canplay', onCanPlay)
      a.removeEventListener('error', onErr); a.removeEventListener('ended', onEnd)
      a.removeEventListener('play', onPlay); a.removeEventListener('pause', onPause)
    }
  },[currentIndex, isYoutube])

  useEffect(()=>{
    if(isYoutube) { setMode("youtube"); setPlaying(false); setLoading(false); setProgress(0); }
    else { setMode("audio"); setError(""); setLoading(true); audioRef.current?.load() }
  },[currentIndex, track, isYoutube])

  useEffect(()=>{ if(audioRef.current && !isYoutube) audioRef.current.volume = volume },[volume])

  const toggle = async ()=>{
    if(isYoutube){
      // youtube iframe autoplays via src change, just toggle UI state
      setPlaying(p=>!p)
      return
    }
    const a = audioRef.current
    if(!a || !track) return
    setError("")
    if(playing){ a.pause(); }
    else {
      try{ setLoading(true); await a.play() }catch(e){ setError("Browser blocked autoplay — click ▶ again. " + (e.message||"")); setLoading(false) }
    }
  }
  const seek = (e)=>{
    const v = Number(e.target.value)
    if(!isYoutube && audioRef.current){ audioRef.current.currentTime = v; setProgress(v) }
  }
  const next = ()=> setIndex(i=> Math.min(queue.length-1, i+1))
  const prev = ()=> setIndex(i=> Math.max(0, i-1))

  if(!track) return (
    <div className="rounded-[24px] bg-white/[0.06] backdrop-blur-xl border border-white/10 p-6 text-center">
      <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xl">♪</div>
      <p className="text-sm text-white/60 mt-3">No track yet — describe mood → <b className="text-white">Recommend + Play</b></p>
    </div>
  )

  return (
    <div className="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-zinc-900 via-[#1a0f2e] to-black border border-white/10 shadow-[0_25px_80px_rgba(0,0,0,0.6),inset_0_1px_0_rgba(255,255,255,0.1)]">
      <div className="absolute -top-32 -right-32 w-80 h-80 bg-gradient-to-br from-violet-600/30 to-fuchsia-600/30 blur-[60px] rounded-full pointer-events-none animate-pulse" />
      <div className="absolute -bottom-32 -left-32 w-80 h-80 bg-gradient-to-br from-indigo-600/25 to-violet-600/25 blur-[60px] rounded-full pointer-events-none" />

      {/* audio or youtube */}
      {!isYoutube ? (
        <audio ref={audioRef} src={track.preview_url} preload="auto" />
      ) : (
        <div className="relative bg-black">
          {mode === "youtube" && youtubeId ? (
            <iframe
              width="100%" height="220"
              src={`https://www.youtube.com/embed/${youtubeId}?autoplay=${playing?1:0}&rel=0&modestbranding=1`}
              title={track.title}
              allow="autoplay; encrypted-media"
              allowFullScreen
              className="w-full"
              style={{border:0}}
            />
          ) : null}
          {/* hidden audio fallback also */}
          <audio ref={audioRef} src={track.preview_url} preload="auto" style={{display:'none'}} />
        </div>
      )}

      <div className="relative p-5 flex items-center gap-4">
        {track.artwork_url ? (
          <img src={track.artwork_url.replace('100x100','200x200')} alt={track.title} className="w-20 h-20 rounded-[18px] object-cover shadow-[0_12px_30px_rgba(0,0,0,0.5)] shrink-0 border border-white/10" />
        ) : (
          <div className="relative w-20 h-20 rounded-[18px] bg-gradient-to-br from-violet-500 via-fuchsia-500 to-indigo-600 flex items-center justify-center shadow-[0_12px_30px_rgba(139,92,246,0.5)] shrink-0 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-tr from-white/20 to-transparent" />
            <span className="relative text-3xl text-white">♫</span>
          </div>
        )}
        <div className="min-w-0 flex-1">
          <div className="text-white font-black text-[16px] truncate flex items-center gap-2">
            {track.title}
            {track.language==='ta' && <span className="text-[10px] bg-orange-500 text-white px-1.5 py-0.5 rounded-full">TA</span>}
            {track.source==='itunes' && <span className="text-[10px] bg-white text-black px-1.5 py-0.5 rounded-full font-black">iTunes • original</span>}
            {isYoutube && !track.artwork_url && <span className="text-[10px] bg-red-600 text-white px-1.5 py-0.5 rounded-full">YouTube</span>}
            {track.source!=='itunes' && !isYoutube && <span className="text-[10px] bg-white/10 text-white/60 border border-white/10 px-1.5 py-0.5 rounded-full">demo</span>}
          </div>
          <div className="text-white/70 text-xs truncate">{track.artist} {track.album ? `· ${track.album}` : ''} · {track.features?.genre}</div>
          <div className="inline-flex items-center gap-1.5 mt-1.5">
            <span className="text-[10px] uppercase bg-white text-black px-2 py-0.5 rounded-full font-bold">{track.emotional_role}</span>
            <span className="text-[11px] text-white/50 truncate">{track.reason}</span>
          </div>
        </div>
        <div className="hidden sm:block text-right">
          <div className="text-[11px] text-white/60 font-mono">{track.features?.tempo} BPM</div>
          <div className="text-[11px] text-emerald-300">match {(track.match_score*100).toFixed(0)}%</div>
        </div>
      </div>

      {/* waveform only for audio mode */}
      {!isYoutube && (
        <div className="relative px-5">
          <canvas ref={canvasRef} width={600} height={36} className="w-full h-9 rounded-xl bg-black/25 border border-white/5" />
          {loading && <div className="absolute inset-0 flex items-center justify-center"><span className="text-xs bg-black/60 backdrop-blur px-3 py-1 rounded-full text-white/80 border border-white/10">Loading audio...</span></div>}
        </div>
      )}
      {isYoutube && (
        <div className="px-5">
          <div className="rounded-xl bg-white/5 border border-white/10 p-2.5 flex items-center justify-between">
            <span className="text-xs text-white/70">▶ Full proper song via YouTube (official video)</span>
            <a href={track.youtube_url} target="_blank" rel="noreferrer" className="text-xs bg-white text-black px-3 py-1 rounded-full font-bold">Open YouTube</a>
          </div>
        </div>
      )}

      <div className="relative px-5 pt-3">
        <div className="relative h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full" style={{width: `${duration? (progress/duration)*100:0}%`}} />
          <input type="range" min={0} max={duration|| (track.duration_ms/1000) || 100} step={0.5} value={progress} onChange={seek} disabled={isYoutube} className="absolute inset-0 w-full opacity-0 cursor-pointer disabled:cursor-not-allowed" />
        </div>
        <div className="flex justify-between text-[11px] font-mono text-white/50 mt-1.5">
          <span>{Math.floor(progress/60)}:{String(Math.floor(progress%60)).padStart(2,'0')}</span>
          <span>{Math.floor((duration||track.duration_ms/1000)/60)}:{String(Math.floor((duration||track.duration_ms/1000)%60)).padStart(2,'0')}</span>
        </div>
      </div>

      <div className="relative flex items-center justify-between px-5 pb-5 pt-1">
        <div className="flex items-center gap-2">
          <button onClick={prev} disabled={currentIndex===0} className="w-9 h-9 rounded-full bg-white/[0.08] border border-white/10 text-white flex items-center justify-center disabled:opacity-40">⏮</button>
          <button onClick={toggle} className="w-14 h-14 rounded-full bg-white text-black flex items-center justify-center shadow-[0_12px_30px_rgba(255,255,255,0.35)] hover:scale-[1.06] transition text-lg font-black">
            {playing ? '❚❚' : '▶'}
          </button>
          <button onClick={next} disabled={currentIndex===queue.length-1} className="w-9 h-9 rounded-full bg-white/[0.08] border border-white/10 text-white flex items-center justify-center disabled:opacity-40">⏭</button>
          <span className="text-xs font-mono text-white/60 ml-2 bg-white/5 border border-white/10 px-2.5 py-1 rounded-full">{currentIndex+1} / {queue.length}</span>
          <button onClick={()=> setMode(m=> m==='youtube' ? 'audio' : 'youtube')} className="hidden md:inline text-[11px] bg-white/10 border border-white/10 text-white px-2.5 py-1 rounded-full">
            {mode==='youtube' ? 'Switch to MP3 demo' : 'Switch to YouTube proper'}
          </button>
        </div>
        <div className="flex items-center gap-3">
          {error && <span className="hidden lg:inline text-[11px] text-amber-300 max-w-[220px] truncate bg-amber-500/10 border border-amber-500/20 px-2 py-1 rounded-full">{error}</span>}
          {!isYoutube && (
            <div className="flex items-center gap-2 bg-black/30 border border-white/10 rounded-full px-3 py-1.5">
              <span className="text-xs">🔊</span>
              <input type="range" min={0} max={1} step={0.05} value={volume} onChange={e=>setVolume(Number(e.target.value))} className="w-20 accent-violet-500 h-1" />
            </div>
          )}
        </div>
      </div>
      {error && <div className="lg:hidden mx-5 mb-4 text-[11px] text-amber-200 bg-amber-500/10 border border-amber-500/20 p-2 rounded-xl">{error}</div>}
    </div>
  )
}
