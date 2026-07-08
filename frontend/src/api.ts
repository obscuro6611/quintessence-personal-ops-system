const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export function token(){ return localStorage.getItem('quint_token') || ''; }
export async function login(username:string,password:string){ const r=await fetch(`${API}/auth/login`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,password})}); if(!r.ok) throw new Error('Login failed'); const j=await r.json(); localStorage.setItem('quint_token',j.access_token); return j; }
export async function get(path:string){ const r=await fetch(`${API}${path}`,{headers:{Authorization:`Bearer ${token()}`}}); if(!r.ok) throw new Error(await r.text()); return r.json(); }
export async function post(path:string,data:any){ const r=await fetch(`${API}${path}`,{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token()}`},body:JSON.stringify(data)}); if(!r.ok) throw new Error(await r.text()); return r.json(); }
export async function uploadEvidence(form:FormData){ const r=await fetch(`${API}/evidence/upload`,{method:'POST',headers:{Authorization:`Bearer ${token()}`},body:form}); if(!r.ok) throw new Error(await r.text()); return r.json(); }
