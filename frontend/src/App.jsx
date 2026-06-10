import { useState, useEffect } from 'react'
import UploadSection from './components/UploadSection'
import ProgressTracker from './components/ProgressTracker'
import Dashboard from './components/Dashboard'

function App() {
  const [appState, setAppState] = useState('idle') // idle, uploading, analyzing, completed, error
  const [jobId, setJobId] = useState(null)
  const [reportData, setReportData] = useState(null)
  const [progressMsg, setProgressMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')

  const handleUpload = async (file) => {
    setAppState('uploading')
    setErrorMsg('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      // Usar la ruta de tu API backend
      const res = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      })
      
      if (!res.ok) {
        throw new Error('Error al subir el archivo')
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
      const eventSource = new EventSource(`http://localhost:8000/api/stream/${jobId}`)
      
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
          const res = await fetch(`http://localhost:8000/api/report/${jobId}`)
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

  return (
    <div className="min-h-screen p-4 md:p-8 flex flex-col items-center">
      <header className="mb-12 text-center mt-8">
        <h1 className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-4">
          CV Analyzer
        </h1>
        <p className="text-slate-400 max-w-xl mx-auto">
          Análisis inteligente de tu currículum usando agentes y LLMs.
        </p>
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
    </div>
  )
}

export default App
