import { useState, useEffect } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { Settings, LogIn, Loader2, Sparkles } from 'lucide-react'
import UploadSection from './components/UploadSection'
import ProgressTracker from './components/ProgressTracker'
import Dashboard from './components/Dashboard'
import ProfileSettings from './components/ProfileSettings'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const { isAuthenticated, isLoading, loginWithRedirect, getAccessTokenSilently, user } = useAuth0()
  const [appState, setAppState] = useState('idle') // idle, uploading, analyzing, completed, error
  const [jobId, setJobId] = useState(null)
  const [reportData, setReportData] = useState(null)
  const [progressMsg, setProgressMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  const handleUpload = async (file, platforms) => {
    setAppState('uploading')
    setErrorMsg('')
    const formData = new FormData()
    formData.append('file', file)
    formData.append('platforms', JSON.stringify(platforms || ['computrabajo']))

    try {
      const token = await getAccessTokenSilently()
      const res = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData,
      })
      
      if (!res.ok) {
        throw new Error('Error al iniciar el análisis')
      }
      
      const data = await res.json()
      setJobId(data.job_id)
      setAppState('analyzing')
    } catch (err) {
      setErrorMsg(err.message)
      setAppState('error')
    }
  }

  useEffect(() => {
    if (appState === 'analyzing' && jobId) {
      const eventSource = new EventSource(`${API_URL}/api/stream/${jobId}`)
      
      eventSource.addEventListener('progress', (e) => {
        try {
          if (e.data) {
            const data = JSON.parse(e.data)
            setProgressMsg(data.message || '')
          }
        } catch (err) {
          console.error('Error parsing progress SSE event:', err)
        }
      })

      eventSource.addEventListener('complete', async (e) => {
        eventSource.close()
        try {
          const token = await getAccessTokenSilently()
          const res = await fetch(`${API_URL}/api/report/${jobId}`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })
          const data = await res.json()
          if (data.status === 'completed') {
            setReportData(data.report)
            setAppState('completed')
          } else {
            throw new Error('El reporte no está listo o falló')
          }
        } catch (err) {
          setErrorMsg(err.message)
          setAppState('error')
        }
      })

      eventSource.addEventListener('error', (e) => {
        eventSource.close()
        let errMsg = 'Error de conexión con el servidor.'
        if (e.data) {
          try {
            const data = JSON.parse(e.data)
            errMsg = data.errors ? data.errors.join(', ') : errMsg
          } catch (err) {
            console.error('Error parsing error SSE event:', err)
          }
        }
        setErrorMsg(errMsg)
        setAppState('error')
      })

      return () => {
        eventSource.close()
      }
    }
  }, [appState, jobId])

  const reset = () => {
    setAppState('idle')
    setJobId(null)
    setReportData(null)
    setProgressMsg('')
    setErrorMsg('')
  }

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
        <p className="text-slate-400 font-medium">Verificando sesión...</p>
      </div>
    )
  }

  // 2. Unauthenticated State (Landing / Login Screen)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-white">
        <div className="w-full max-w-md bg-slate-900/40 border border-slate-800 p-8 rounded-3xl text-center shadow-2xl glass-card relative overflow-hidden">
          <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>
          
          <div className="w-16 h-16 mx-auto bg-blue-600/10 border border-blue-500/20 rounded-2xl flex items-center justify-center mb-6">
            <Sparkles className="w-8 h-8 text-blue-400 animate-pulse" />
          </div>
          
          <h1 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-3">
            CV Analyzer
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed mb-8">
            Optimiza tu perfil, detecta brechas y obtén vacantes automáticas cada semana analizando tu currículum con Inteligencia Artificial.
          </p>
          
          <button 
            onClick={() => loginWithRedirect()}
            className="w-full py-3.5 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl transition-all shadow-lg hover:shadow-blue-500/15 flex items-center justify-center gap-2"
          >
            <LogIn className="w-5 h-5" /> Comenzar Ahora
          </button>
        </div>
      </div>
    )
  }

  // 3. Authenticated Workspace
  return (
    <div className="min-h-screen p-4 md:p-8 flex flex-col items-center">
      <header className="w-full max-w-5xl flex items-center justify-between mb-12 mt-4">
        <div className="flex flex-col">
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            CV Analyzer
          </h1>
          <p className="text-slate-400 text-xs md:text-sm mt-1">
            Análisis inteligente de currículums.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className="flex items-center gap-2 py-2 px-4 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-850 hover:border-slate-700 text-white font-semibold transition-all text-sm cursor-pointer shadow-sm"
          >
            {user?.picture ? (
              <img src={user.picture} alt="" className="w-5 h-5 rounded-full" />
            ) : (
              <Settings className="w-4 h-4 text-slate-400" />
            )}
            Mi Cuenta
          </button>
        </div>
      </header>

      <main className="w-full max-w-5xl flex flex-col items-center">
        {appState === 'idle' || appState === 'uploading' ? (
          <UploadSection onUpload={handleUpload} isUploading={appState === 'uploading'} />
        ) : null}

        {appState === 'analyzing' && (
          <ProgressTracker message={progressMsg} />
        )}

        {appState === 'completed' && reportData && (
          <Dashboard data={reportData} jobId={jobId} onReset={reset} />
        )}

        {appState === 'error' && (
          <div className="glass-card p-8 w-full max-w-lg text-center border-red-500/50">
            <h2 className="text-xl font-bold text-red-400 mb-4">Oops, algo salió mal</h2>
            <p className="text-slate-300 mb-6">{errorMsg}</p>
            <button onClick={reset} className="primary-btn">
              Intentar de nuevo
            </button>
          </div>
        )}
      </main>

      <ProfileSettings 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  )
}

export default App

