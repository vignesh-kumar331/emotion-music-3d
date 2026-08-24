import { useState, useEffect } from 'react'
import api from '../api/client'
export default function Journal(){
  const [text,setText]=useState("")
  const [entries,setEntries]=useState([])
  const [insights,setInsights]=useState(null)
  const load=async()=>{
    try{
      const r=await api.get('/journal')
      setEntries(r.data)
      const ins=await api.get('/journal/insights')
      setInsights(ins.data)
    }catch(e){ if(e.response?.status===401) setEntries([])}
  }
  useEffect(()=>{load()},[])
  const save=async()=>{
    if(!text) return
    try{ await api.post('/journal',{text, analyze:false, tags:[]}); setText(""); load()}catch(e){alert('Login required')}
  }
  const del=async(id)=>{ await api.delete(`/journal/${id}`); load()}
  const exp=async()=>{ const r=await api.get('/journal/export'); const blob=new Blob([JSON.stringify(r.data,null,2)],{type:'application/json'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='mood_export.json'; a.click()}
  return (
    <div className="max-w-3xl mx-auto p-6 space-y-4">
      <div className="bg-white p-5 rounded-xl shadow">
        <h2 className="font-semibold mb-2">Mood Journal</h2>
        <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="Write how you feel today..." className="w-full border rounded p-3 h-24 text-sm"/>
        <button onClick={save} className="mt-2 bg-black text-white px-4 py-1.5 rounded text-sm">Save entry</button>
        <p className="text-xs text-zinc-500 mt-1">You control journal analysis. Enable in Settings to auto-analyze valence/arousal.</p>
      </div>
      {insights && <div className="bg-indigo-50 p-4 rounded text-sm"><b>Insights:</b> {insights.total_entries? `${insights.total_entries} entries · ${JSON.stringify(insights.mood_distribution)} · ${insights.note}`: insights.message}</div>}
      <div className="bg-white p-5 rounded-xl shadow">
        <div className="flex justify-between"><h3 className="font-semibold">Entries</h3><button onClick={exp} className="text-xs underline">Export for professional sharing</button></div>
        <div className="mt-3 space-y-2">
          {entries.map(e=> <div key={e.id} className="border rounded p-3 text-sm"><div className="text-xs text-zinc-500">{new Date(e.timestamp).toLocaleString()} {e.mood && `· ${e.mood}`}</div><div>{e.text}</div><button onClick={()=>del(e.id)} className="text-xs underline mt-1">Delete</button></div>)}
          {!entries.length && <div className="text-xs text-zinc-500">No entries yet.</div>}
        </div>
      </div>
    </div>
  )
}
