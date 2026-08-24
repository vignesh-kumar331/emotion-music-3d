import { useState } from 'react'
import api from '../api/client'
import { useNavigate, Link } from 'react-router-dom'
export default function Login(){
  const [email,setEmail]=useState("demo@emotion.app")
  const [password,setPassword]=useState("demo123")
  const [mode,setMode]=useState("login")
  const nav=useNavigate()
  const submit=async(e)=>{
    e.preventDefault()
    try{
      const url=mode==='login'? '/auth/login':'/auth/register'
      const r=await api.post(url,{email,password, display_name: email.split('@')[0]})
      localStorage.setItem('token', r.data.access_token)
      nav('/')
    }catch(err){ alert(err.response?.data?.detail || err.message)}
  }
  return (
    <div className="max-w-md mx-auto p-6">
      <div className="bg-white p-6 rounded-xl shadow">
        <h2 className="font-semibold">{mode==='login'?'Login':'Register'}</h2>
        <form onSubmit={submit} className="mt-3 space-y-3">
          <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" className="w-full border rounded p-2 text-sm"/>
          <input value={password} onChange={e=>setPassword(e.target.value)} type="password" placeholder="password" className="w-full border rounded p-2 text-sm"/>
          <button className="w-full bg-black text-white rounded p-2 text-sm">{mode==='login'?'Login':'Create account'}</button>
        </form>
        <button onClick={()=>setMode(mode==='login'?'register':'login')} className="text-xs underline mt-2">{mode==='login'?'Need account? Register':'Have account? Login'}</button>
      </div>
    </div>
  )
}
