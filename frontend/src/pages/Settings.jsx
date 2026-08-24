import { useEffect, useState } from 'react'
import api from '../api/client'
export default function Settings(){
  const [prefs,setPrefs]=useState(null)
  const load=async()=>{ try{ const r=await api.get('/preferences'); setPrefs(r.data)}catch(e){ console.error(e)}}
  useEffect(()=>{load()},[])
  const toggle=async(field)=>{ const upd={}; upd[field]=!prefs[field]; const r=await api.put('/preferences',upd); setPrefs(r.data)}
  const reset=async()=>{ if(!confirm('Reset personalization profile and delete emotional history?')) return; await api.delete('/preferences/reset'); load(); alert('Reset complete')}
  if(!prefs) return <div className="p-6 text-sm text-white/70">Login to manage settings. Toggles per spec 30.</div>
  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <div className="rounded-[28px] bg-white/[0.06] backdrop-blur-2xl border border-white/10 p-6 shadow-xl">
        <h2 className="font-black text-white text-lg">Privacy & Personalization</h2>
        <p className="text-xs text-white/50 mt-1">Emotional information is sensitive. Per spec 29-30 you control all signals. Tamil language uses free iTunes API for original studio previews.</p>
        <div className="mt-5 space-y-2 text-sm">
          {[
            ['emotion_detection_enabled','Emotion Detection','Detects valence/arousal'],
            ['personalized_recommendations','Personalized Recommendations','Uses your taste'],
            ['mood_history_enabled','Mood History','Stores emotion events'],
            ['contextual_personalization','Contextual Personalization','Time/activity/weather'],
            ['journal_analysis_enabled','Journal Analysis','Analyzes journal text'],
            ['camera_analysis_enabled','Camera Analysis','Requires consent'],
            ['voice_analysis_enabled','Voice Analysis','Requires consent'],
            ['biometric_enabled','Biometric Integration','Wearable HR/HRV'],
          ].map(([k,label,desc])=>(
            <label key={k} className="flex justify-between items-center rounded-2xl bg-white/[0.04] border border-white/10 px-4 py-3 hover:bg-white/[0.06] transition cursor-pointer">
              <div>
                <div className="font-semibold text-white text-sm">{label}</div>
                <div className="text-xs text-white/40">{desc}</div>
              </div>
              <input type="checkbox" checked={!!prefs[k]} onChange={()=>toggle(k)} className="w-5 h-5 accent-violet-500"/>
            </label>
          ))}
        </div>
        <div className="mt-5 grid grid-cols-2 gap-2">
          <div className="rounded-2xl bg-white/[0.04] border border-white/10 p-3">
            <div className="text-xs font-bold text-white/70 uppercase tracking-widest">Language</div>
            <div className="flex gap-1 mt-2">
              {['ta','en'].map(l=>(
                <button key={l} onClick={async()=>{ await api.put('/preferences', {cultural_prefs:{language:l}}); load() }} className={`px-3 py-1.5 rounded-full text-xs font-black border ${prefs.cultural_prefs?.language===l ? 'bg-white text-black border-white' : 'bg-white/5 text-white/60 border-white/10'}`}>{l==='ta' ? 'Tamil' : 'English'}</button>
              ))}
            </div>
          </div>
          <div className="rounded-2xl bg-gradient-to-br from-violet-600/15 to-fuchsia-600/15 border border-violet-500/20 p-3">
            <div className="text-xs font-bold text-white">Why am I seeing this?</div>
            <button onClick={async()=>{const r=await api.get('/preferences/transparency'); alert(JSON.stringify(r.data,null,2))}} className="mt-2 w-full bg-white text-black px-3 py-1.5 rounded-full text-xs font-black">View transparency</button>
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <button onClick={reset} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-full text-sm font-bold shadow">Reset profile</button>
          <span className="text-xs text-white/30 self-center">Wipes emotion history & taste</span>
        </div>
        <p className="text-xs text-white/30 mt-3">Consent required before camera/mic/biometric (spec 49). Tamil originals via free <b className="text-white/60">iTunes Search API</b> (30s studio previews, no key).</p>
      </div>
    </div>
  )
}
