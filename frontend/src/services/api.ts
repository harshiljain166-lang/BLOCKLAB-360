const BASE=import.meta.env.VITE_API_URL||'http://127.0.0.1:8000';
export async function api<T=any>(path:string,options:RequestInit={}):Promise<T>{const res=await fetch(`${BASE}/api${path}`,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});const data=await res.json().catch(()=>({detail:res.statusText}));if(!res.ok)throw new Error(data.detail||data.error||`Request failed (${res.status})`);return data as T;}
export const post=(path:string,body:any={})=>api(path,{method:'POST',body:JSON.stringify(body)});
export const wsUrl=()=>BASE.replace(/^http/,'ws')+'/ws';
