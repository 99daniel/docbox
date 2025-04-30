import React, { useState, useEffect, ReactNode } from 'react'
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
  Link,
  useNavigate,
  RouteObject
} from 'react-router-dom'
import styles from './App.module.css'

// --- API utility ------------------------------------------------------------
async function apiRequest<T>(
  path: string,
  method = 'GET',
  body?: any,
  token?: string
): Promise<T> {
  const headers: Record<string,string> = {}
  let payload: any
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (body instanceof FormData) payload = body
  else if (body instanceof URLSearchParams) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    payload = body.toString()
  } else if (body) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }
  const res = await fetch(`http://localhost:8000${path}`, {
    method, headers, body: payload
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Error ${res.status}`)
  }
  return res.json()
}

// --- Auth Context ----------------------------------------------------------
type AuthContextType = {
  token: string | null
  login: (t: string) => void
  logout: () => void
}
const AuthContext = React.createContext<AuthContextType|undefined>(undefined)

function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string|null>(localStorage.getItem('token'))
  const login = (t: string) => {
    localStorage.setItem('token', t)
    setToken(t)
  }
  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }
  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
function useAuth() {
  const ctx = React.useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}

// --- PrivateRoute ----------------------------------------------------------
function PrivateRoute({ element }: { element: JSX.Element }) {
  const { token } = useAuth()
  return token ? element : <Navigate to="/login" replace />
}

// --- Register ---------------------------------------------------------------
function Register() {
  const [user, setUser] = useState('')
  const [pass, setPass] = useState('')
  const [err, setErr] = useState<string|null>(null)
  const nav = useNavigate()

  const submit = async () => {
    try {
      await apiRequest('/auth/register','POST',{username:user,password:pass})
      nav('/login')
    } catch(e:any) {
      setErr(e.message)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2>Register</h2>
        {err && <p style={{color:'red'}}>{err}</p>}
        <label>Username</label>
        <input
          className={styles.input}
          value={user}
          onChange={e=>setUser(e.target.value)}
        />
        <label>Password</label>
        <input
          type="password"
          className={styles.input}
          value={pass}
          onChange={e=>setPass(e.target.value)}
        />
        <button className={styles.button} onClick={submit}>
          Create Account
        </button>
        <p>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}

// --- Login ------------------------------------------------------------------
function Login() {
  const [user, setUser] = useState('')
  const [pass, setPass] = useState('')
  const [err, setErr] = useState<string|null>(null)
  const { login } = useAuth()
  const nav = useNavigate()

  const submit = async () => {
    try {
      const data = new URLSearchParams({ username: user, password: pass })
      const res = await apiRequest<{access_token:string}>(
        '/auth/login','POST',data
      )
      login(res.access_token)
      nav('/dashboard')
    } catch(e:any) {
      setErr(e.message)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2>Login</h2>
        {err && <p style={{color:'red'}}>{err}</p>}
        <label>Username</label>
        <input
          className={styles.input}
          value={user}
          onChange={e=>setUser(e.target.value)}
        />
        <label>Password</label>
        <input
          type="password"
          className={styles.input}
          value={pass}
          onChange={e=>setPass(e.target.value)}
        />
        <button className={styles.button} onClick={submit}>
          Sign In
        </button>
      </div>
    </div>
  )
}

// --- Dashboard -------------------------------------------------------------
interface Doc { id:number; filename:string; ocr_status:string }

function Dashboard() {
  const { token, logout } = useAuth()
  const [docs,setDocs] = useState<Doc[]>([])
  const [file,setFile] = useState<File|null>(null)
  const [sel,setSel] = useState<{filename:string;text:string}|null>(null)

  useEffect(()=>{
    apiRequest<Doc[]>('/documents','GET',null,token!)
      .then(setDocs)
      .catch(console.error)
  },[token])

  const upload = async()=>{
    if(!file) return
    const form = new FormData()
    form.append('file',file)
    await apiRequest<Doc>('/documents/upload','POST',form,token!)
    const updated = await apiRequest<Doc[]>('/documents','GET',null,token!)
    setDocs(updated)
  }

  const view = async(id:number)=>{
    const res = await apiRequest<{filename:string;text:string}>(
      `/documents/${id}/result`,'GET',null,token!
    )
    setSel(res)
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>My Documents</h1>
        <button className={styles.button} onClick={logout}>Logout</button>
      </header>

      <section className={styles.card}>
        <h2>Upload New Document</h2>
        <input
          type="file"
          onChange={e=>setFile(e.target.files?.[0]||null)}
        />
        <button
          className={styles.button}
          style={{marginTop:'0.5rem'}}
          onClick={upload}
        >
          Upload
        </button>
      </section>

      <section className={styles.grid} style={{marginTop:'1rem'}}>
        {docs.map(d=>(
          <div key={d.id} className={styles.card}>
            <p><strong>{d.filename}</strong></p>
            <p>Status: {d.ocr_status}</p>
            <button
              className={styles.button}
              onClick={()=>view(d.id)}
            >
              View
            </button>
          </div>
        ))}
      </section>

      {sel && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <button
              className={styles.closeBtn}
              onClick={()=>setSel(null)}
            >
              &times;
            </button>
            <div className={styles.modalBody}>
              <div className={styles.imageWrapper}>
                <ZoomableImage
                  src={`http://localhost:8000/storage/${sel.filename}`}
                  alt={sel.filename}
                />
              </div>
              <div className={styles.textWrapper}>
                <pre style={{whiteSpace:'pre-wrap'}}>{sel.text}</pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// --- ZoomableImage ---------------------------------------------------------
function ZoomableImage({
  src, alt
}: {
  src:string, alt?:string
}) {
  const [zoom, setZoom] = useState(false)
  return (
    <img
      src={src}
      alt={alt}
      onClick={()=>setZoom(z=>!z)}
      className={`${styles.zoomable} ${zoom?styles.zoomed:''}`}
    />
  )
}

// --- Routes & Export -------------------------------------------------------
const routes: RouteObject[] = [
  { path:'/register', element:<Register/> },
  { path:'/login',    element:<Login/>    },
  { path:'/dashboard',element:<PrivateRoute element={<Dashboard/>}/> },
  { path:'*',         element:<Navigate to='/login' replace/> }
]

export default function App() {
  const router = createBrowserRouter(routes)
  return (
    <AuthProvider>
      <RouterProvider router={router}/>
    </AuthProvider>
  )
}
