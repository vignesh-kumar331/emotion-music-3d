import { useState } from 'react'
import api from '../api/client'
import EmotionOrb from '../components/EmotionOrb'
import AudioPlayer from '../components/AudioPlayer'

const EMOTIONS = ["joy","sadness","anger","fear","surprise","calm","anxiety","excitement","loneliness","nostalgia","melancholy","hope","frustration","restlessness","boredom","gratitude","motivation","peacefulness"]
const GOALS = ["Stay with my mood","Feel understood","Calm down","Feel hopeful","Become energized","Distract myself","Surprise me"]

export default function Companion(){
  const [text,setText]=useState("")
  const [manualEmotion,setManualEmotion]=useState("")
  const [intensity,setIntensity]=useState(70)
  const [goal,setGoal]=useState("Feel understood")
  const [activity,setActivity]=useState("")
  const [language,setLanguage]=useState("ta") // default Tamil per user request — switch to 'en' for English, '' for mixed
  const [result,setResult]=useState(null)
  const [loading,setLoading]=useState(false)
  const [analysis,setAnalysis]=useState(null)
  const [safetyMsg,setSafetyMsg]=useState("")
  const [queue,setQueue]=useState([])
  const [idx,setIdx]=useState(0)

  const analyze = async ()=>{
    try{
      const r=await api.post('/emotion/analyze-text',{text, include_safety:true})
      setAnalysis(r.data)
    }catch(e){ console.error(e)}
  }

  const recommend = async ()=>{
    setLoading(true); setSafetyMsg("")
    try{
      let body={}
      if(manualEmotion){
        body.emotion={primary_emotion: manualEmotion, secondary_emotions:[], valence: 0, arousal: intensity/100, confidence:0.9, emotions:[{label: manualEmotion, score: intensity/100}]}
      } else if(text){
        body.text=text
      } else {
        body.text="calm"
      }
      body.listening_goal=goal
      body.activity=activity||undefined
      if(language) body.language=language
      body.limit=8
      const r=await api.post('/recommendations', body)
      setResult(r.data)
      setQueue(r.data.recommendations)
      setIdx(0)
      if(r.data.explanation.includes("crisis helpline")) setSafetyMsg(r.data.explanation)
    }catch(e){ console.error(e); alert(e.response?.data?.detail || e.message)}
    setLoading(false)
  }

  const feedback = async (track_id, type)=>{
    try{ await api.post('/recommendations/feedback',{track_id, feedback_type:type}); alert(`Feedback ${type} recorded → ranking updated`)}
    catch(e){ if(e.response?.status===401) alert('Login to save feedback'); else alert(e.message)}
  }

  const valence = analysis?.emotion?.valence ?? result?.mood_summary?.valence ?? 0
  const arousal = analysis?.emotion?.arousal ?? result?.mood_summary?.arousal ?? 0.4
  const primary = analysis?.emotion?.primary_emotion ?? result?.mood_summary?.primary_emotion ?? manualEmotion ?? 'calm'

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-6">
      {/* HERO */}
      <div className="mb-6 rounded-[28px] bg-gradient-to-br from-violet-600 via-fuchsia-500 to-cyan-400 p-[1px] shadow-[0_20px_60px_rgba(139,92,246,0.35)]">
        <div className="rounded-[27px] bg-[#0b0b12]/90 backdrop-blur-xl p-5 md:p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-[28px] font-black tracking-tight bg-gradient-to-r from-white via-violet-200 to-fuchsia-200 bg-clip-text text-transparent">How are you feeling today?</h1>
            <p className="text-sm text-white/60 mt-1 max-w-xl">Describe it, pick from the 3D wheel, choose a music goal → get a <span className="text-white font-semibold">valence/arousal</span>-matched playlist with <span className="text-emerald-300">one-click playback</span>. Tamil songs prioritized when Tamil selected.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <span className="text-[11px] tracking-widest uppercase bg-white text-black px-3 py-1.5 rounded-full font-black">LIVE 3D</span>
            <div className="flex rounded-full bg-black/40 border border-white/10 p-1 backdrop-blur">
              {[
                ['ta','Tamil'],
                ['en','English'],
                ['','Mix'],
              ].map(([val,label])=> (
                <button key={val} onClick={()=>setLanguage(val)} className={`px-3 py-1 text-xs font-black rounded-full transition ${language===val ? 'bg-white text-black shadow' : 'text-white/60 hover:text-white'}`}>{label}</button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-[380px_1fr] gap-6 mb-6">
        <div className="rounded-[28px] bg-gradient-to-br from-white/[0.08] to-white/[0.03] backdrop-blur-2xl border border-white/10 p-6 shadow-[0_25px_80px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.08)] flex flex-col items-center relative overflow-hidden" style={{transform:'perspective(1000px) rotateY(1.5deg)'}}>
          <div className="absolute -top-24 -right-24 w-64 h-64 bg-violet-600/20 blur-[50px] rounded-full pointer-events-none" />
          <h2 className="text-sm font-black tracking-[0.14em] uppercase text-white/80 mb-3">Emotion Orb — 3D</h2>
          <div className="rounded-[24px] bg-black/20 border border-white/10 p-3 shadow-inner">
            <EmotionOrb valence={valence} arousal={arousal} primary={primary} size={260} />
          </div>
          <p className="text-xs text-white/40 mt-3 text-center">Drag · Orbit · Color = valence · Motion = arousal</p>
          <div className="mt-4 w-full grid grid-cols-2 gap-2 text-xs">
            <div className="rounded-2xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 p-3 text-center backdrop-blur">
              <div className="text-white/50 text-[11px] tracking-widest uppercase">Valence</div><div className="text-white font-black text-lg">{valence.toFixed(2)}</div>
            </div>
            <div className="rounded-2xl bg-gradient-to-br from-cyan-500/15 to-violet-500/15 border border-cyan-500/20 p-3 text-center backdrop-blur">
              <div className="text-white/50 text-[11px] tracking-widest uppercase">Arousal</div><div className="text-white font-black text-lg">{arousal.toFixed(2)}</div>
            </div>
          </div>
          <div className="mt-3 w-full rounded-2xl bg-white text-black p-3 text-center">
            <div className="text-[11px] tracking-widest uppercase opacity-60">Current</div>
            <div className="font-black capitalize">{primary} <span className="font-normal opacity-60">· conf {(analysis?.emotion?.confidence ?? result?.mood_summary?.confidence ?? 0.9).toFixed(2)}</span></div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-[28px] bg-white/[0.06] backdrop-blur-2xl border border-white/10 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.4)] relative overflow-hidden" style={{transform:'perspective(1000px) rotateY(-1deg)'}}>
            <div className="absolute inset-0 bg-gradient-to-br from-violet-500/[0.06] via-transparent to-fuchsia-500/[0.06] pointer-events-none" />
            <h2 className="relative font-black text-white flex items-center gap-2"><span className="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center text-xs">✎</span> Tell me in your words</h2>
            <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="I'm feeling exhausted...  I'm really excited today...  I don't know what I'm feeling..." className="relative w-full mt-3 bg-black/30 border border-white/10 rounded-2xl p-4 h-28 text-sm text-white placeholder:text-white/30 focus:outline-none focus:border-violet-500/40 focus:bg-black/40 transition"/>
            <div className="relative flex flex-wrap gap-2 mt-4">
              <button onClick={analyze} className="px-5 py-2.5 text-sm bg-white text-black rounded-full font-black shadow-[0_10px_20px_rgba(255,255,255,0.2)] hover:scale-[1.02] active:scale-[0.99] transition">Analyze text</button>
              <button onClick={recommend} disabled={loading} className="px-6 py-2.5 text-sm bg-gradient-to-br from-violet-600 via-fuchsia-600 to-violet-600 text-white rounded-full font-black shadow-[0_12px_30px_rgba(139,92,246,0.45)] hover:shadow-[0_16px_40px_rgba(139,92,246,0.55)] disabled:opacity-50 transition flex items-center gap-2">
                {loading ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : '▶'} Recommend + Play
              </button>
              <span className="text-[11px] text-white/40 self-center hidden sm:inline">Explicit words beat inferred signals</span>
            </div>
            {analysis && (
              <div className="relative mt-4 rounded-2xl overflow-hidden bg-gradient-to-br from-zinc-900 to-black border border-white/10 p-[1px]">
                <div className="bg-black/40 backdrop-blur p-4 rounded-[15px]">
                  <div className="text-sm text-white"><span className="text-white/50">Detected:</span> <b className="capitalize">{analysis.emotion.primary_emotion || 'neutral'}</b> · v{analysis.emotion.valence} a{analysis.emotion.arousal} · <span className="text-emerald-300">conf {analysis.emotion.confidence}</span></div>
                  <div className="text-xs text-white/50 mt-1">Intent: {analysis.intent} {analysis.safety?.is_crisis && <span className="text-red-300 font-black">· Crisis</span>}</div>
                  <div className="mt-2 flex flex-wrap gap-1.5">{analysis.emotion.emotions?.map(e=> <span key={e.label} className="bg-white text-black px-2.5 py-1 rounded-full text-xs font-bold">{e.label} {e.score}</span>)}</div>
                </div>
              </div>
            )}
          </div>

          {queue.length>0 && <AudioPlayer queue={queue} currentIndex={idx} setIndex={setIdx} onEnded={()=> setIdx(i=> Math.min(queue.length-1, i+1)) } /> }
          {queue.length===0 && <div className="rounded-[24px] bg-gradient-to-br from-violet-600/10 to-fuchsia-600/10 border border-violet-500/20 p-4 text-center backdrop-blur"><p className="text-sm text-white font-semibold">Ready to play</p><p className="text-xs text-white/50">Your recommendations will appear here as a playable queue with waveform</p></div>}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="rounded-[28px] bg-white/[0.06] backdrop-blur-2xl border border-white/10 p-6 shadow-xl relative overflow-hidden">
            <div className="absolute -top-20 -left-20 w-60 h-60 bg-fuchsia-600/10 blur-[40px] rounded-full pointer-events-none" />
            <h3 className="relative font-black text-sm tracking-wide text-white flex items-center gap-2"><span className="w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-[11px]">◈</span> Emotion Wheel — highest priority</h3>
            <p className="relative text-xs text-white/40 mt-1">Tap one — it overrides text/voice/face signals</p>
            <div className="relative flex flex-wrap gap-1.5 mt-4">
              {EMOTIONS.map(e=> <button key={e} onClick={()=>setManualEmotion(e)} className={`px-3.5 py-2 text-xs rounded-full border font-semibold backdrop-blur transition-all ${manualEmotion===e?'bg-white text-black border-white shadow-[0_10px_20px_rgba(255,255,255,0.25)] scale-[1.05] rotate-[0.5deg]':'bg-white/[0.06] text-white/80 border-white/10 hover:bg-white/10 hover:text-white hover:scale-[1.02]'}`}>{e}</button>)}
            </div>
            {manualEmotion && <div className="relative mt-5 rounded-2xl bg-black/30 border border-white/10 p-4">
              <div className="flex items-center justify-between"><label className="text-xs font-bold tracking-widest uppercase text-white/70">Intensity {intensity}%</label><button onClick={()=>setManualEmotion("")} className="text-xs bg-white text-black px-3 py-1 rounded-full font-bold">Clear</button></div>
              <input type="range" min="10" max="100" value={intensity} onChange={e=>setIntensity(e.target.value)} className="w-full mt-2 accent-violet-500"/>
            </div>}
          </div>

          <div className="rounded-[28px] bg-white/[0.06] backdrop-blur-2xl border border-white/10 p-6 shadow-xl">
            <h3 className="font-black text-sm text-white flex items-center gap-2"><span className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-[11px]">♫</span> Music goal</h3>
            <div className="flex flex-wrap gap-2 mt-4">
              {GOALS.map(g=> <button key={g} onClick={()=>setGoal(g)} className={`px-4 py-2 text-xs rounded-full border font-bold transition ${goal===g?'bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white border-transparent shadow-[0_8px_20px_rgba(139,92,246,0.4)] scale-[1.02]':'bg-white/[0.05] text-white/70 border-white/10 hover:bg-white/10 hover:text-white'}`}>{g}</button>)}
            </div>
            <div className="mt-4 grid grid-cols-[140px_1fr] gap-3">
              <select value={activity} onChange={e=>setActivity(e.target.value)} className="bg-black/40 border border-white/10 rounded-full px-3 py-2.5 text-sm text-white">
                <option value="" className="bg-zinc-900">Activity</option>
                <option value="studying" className="bg-zinc-900">Studying</option><option value="exercising" className="bg-zinc-900">Exercising</option><option value="relaxing" className="bg-zinc-900">Relaxing</option><option value="commuting" className="bg-zinc-900">Commuting</option><option value="meditation" className="bg-zinc-900">Meditation</option>
              </select>
              <div className="text-[11px] leading-tight text-white/40 self-center bg-white/5 border border-white/5 rounded-full px-3 py-2">“I’m angry. Give me something energetic.” → honors arousal</div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {safetyMsg && <div className="rounded-[20px] bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-200 backdrop-blur">{safetyMsg}</div>}
          {result && (
            <div className="rounded-[28px] bg-white/[0.06] backdrop-blur-2xl border border-white/10 overflow-hidden shadow-xl" style={{transform:'perspective(1000px) rotateY(-0.8deg)'}}>
              <div className="h-1 w-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-cyan-400" />
              <div className="p-6">
                <div className="flex justify-between items-start gap-3">
                  <div>
                    <h3 className="font-black text-white">Mood summary</h3>
                    <p className="text-sm capitalize font-semibold bg-gradient-to-r from-violet-300 to-fuchsia-300 bg-clip-text text-transparent">{result.mood_summary.primary_emotion || 'mixed'} {result.mood_summary.secondary_emotions?.length? `+ ${result.mood_summary.secondary_emotions.join(', ')}`:''}</p>
                    <p className="text-xs font-mono text-white/40">v{result.mood_summary.valence} · a{result.mood_summary.arousal} · conf {result.mood_summary.confidence}</p>
                  </div>
                  <span className="text-xs bg-white text-black px-3 py-1.5 rounded-full font-black shrink-0">{result.listening_goal}</span>
                </div>
                <div className="mt-4 rounded-2xl bg-gradient-to-br from-violet-500/10 to-fuchsia-500/10 border border-violet-500/20 p-4">
                  <p className="text-sm text-white/90 leading-relaxed">{result.explanation}</p>
                  <p className="text-xs text-white/40 mt-2 font-mono">Progression: {result.progression.join(' → ')}</p>
                </div>
                <div className="mt-4 space-y-2.5 max-h-[380px] overflow-auto pr-1">
                  {result.recommendations.map((r,i)=>(
                    <div key={r.track_id} onClick={()=> setIdx(i)} className={`group relative overflow-hidden border rounded-[18px] p-3.5 flex justify-between items-center cursor-pointer transition-all ${i===idx?'bg-white text-black border-white shadow-[0_16px_40px_rgba(255,255,255,0.25)] scale-[1.015]':'bg-white/[0.04] border-white/10 text-white hover:bg-white/[0.08] hover:border-white/15 hover:scale-[1.01]'}`}>
                      {i===idx && <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-violet-500 to-fuchsia-500" />}
                      <div className="min-w-0 flex gap-3 items-center">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 font-black ${i===idx ? 'bg-black text-white' : 'bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white'}`}>{i+1}</div>
                        <div className="min-w-0">
                          <div className="font-black text-sm truncate leading-tight">{r.title} <span className={`font-normal ${i===idx?'text-zinc-500':'text-white/50'}`}>— {r.artist}</span> {i===idx && <span className="ml-1 inline-flex items-center gap-1 text-[10px] bg-black text-white px-1.5 py-0.5 rounded-full">▶ PLAYING</span>}</div>
                          <div className={`text-xs font-mono flex items-center gap-1.5 ${i===idx?'text-zinc-500':'text-white/40'}`}><span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${r.language==='ta' ? 'bg-orange-500 text-white' : 'bg-white/10 text-white/60'}`}>{r.language==='ta' ? 'TA' : 'EN'}</span> {r.features.genre} · {r.features.tempo} BPM · e{r.features.energy} · v{r.features.valence}</div>
                          <div className="text-xs mt-1 truncate"><span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${i===idx?'bg-black text-white':'bg-white/10 text-white/70 border border-white/10'}`}>{r.emotional_role}</span> <span className={i===idx?'text-zinc-600':'text-white/50'}>{r.reason}</span></div>
                        </div>
                      </div>
                      <div className="flex flex-col gap-1 ml-3 shrink-0">
                        <button onClick={(e)=>{e.stopPropagation(); feedback(r.track_id,'like')}} className={`w-8 h-8 rounded-full flex items-center justify-center text-xs border ${i===idx?'border-black/10 hover:bg-black/5':'border-white/10 hover:bg-white/10 text-white bg-white/5'}`}>♥</button>
                        <button onClick={(e)=>{e.stopPropagation(); setIdx(i); setTimeout(()=> document.querySelector('audio')?.play().catch(()=>{}), 80)}} className={`text-[11px] font-black px-3 py-1.5 rounded-full ${i===idx?'bg-black text-white':'bg-white text-black shadow-md'}`}>Play</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          {!result && <div className="rounded-[28px] bg-white/[0.04] border border-white/10 p-8 text-center backdrop-blur"><div className="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xl">♪</div><p className="text-sm text-white font-bold mt-3">No recommendations yet</p><p className="text-xs text-white/40 mt-1">Describe mood or tap the orb wheel → <b className="text-white">Recommend + Play</b> — streams <b className="text-white">original iTunes studio previews</b> (30s, no demo), click any card to switch track</p></div>}
        </div>
      </div>
    </div>
  )
}
