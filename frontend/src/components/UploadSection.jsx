import { useState, useRef } from 'react'
import { UploadCloud, File, X } from 'lucide-react'

export default function UploadSection({ onUpload, isUploading }) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const inputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'application/pdf') {
        setSelectedFile(file)
      } else {
        alert('Solo se permiten archivos PDF')
      }
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const [platforms, setPlatforms] = useState(['computrabajo'])

  const handlePlatformChange = (platform) => {
    if (platforms.includes(platform)) {
      if (platforms.length > 1) {
        setPlatforms(platforms.filter(p => p !== platform))
      }
    } else {
      setPlatforms([...platforms, platform])
    }
  }

  const handleUploadClick = () => {
    if (selectedFile) {
      onUpload(selectedFile, platforms)
    }
  }

  return (
    <div className="glass-card p-8 md:p-12 w-full flex flex-col items-center">
      <h2 className="text-2xl font-bold mb-2">Subí tu CV en formato PDF</h2>
      <p className="text-slate-400 text-center max-w-lg mb-8">
        El sistema analizará tu CV, buscará ofertas laborales relevantes y generará recomendaciones personalizadas para mejorar tu empleabilidad.
      </p>

      {!selectedFile ? (
        <div
          className={`w-full max-w-xl p-10 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-colors cursor-pointer
            ${dragActive ? 'border-primary bg-primary/10' : 'border-slate-600 hover:border-slate-400 hover:bg-slate-800/50'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current.click()}
        >
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            accept="application/pdf"
            onChange={handleChange}
          />
          <UploadCloud className={`w-16 h-16 mb-4 ${dragActive ? 'text-primary' : 'text-slate-500'}`} />
          <p className="text-lg font-medium">Arrastrá o seleccioná tu CV</p>
          <p className="text-sm text-slate-500 mt-2">Solo archivos PDF (Max: 10MB)</p>
        </div>
      ) : (
        <div className="w-full max-w-xl p-6 border border-slate-700 rounded-xl flex flex-col items-center bg-slate-800/30">
          <div className="flex items-center gap-4 mb-6 p-4 bg-slate-800 rounded-lg w-full">
            <File className="w-10 h-10 text-primary" />
            <div className="flex-1 overflow-hidden">
              <p className="font-medium truncate" title={selectedFile.name}>{selectedFile.name}</p>
              <p className="text-sm text-slate-400">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button 
              onClick={() => setSelectedFile(null)}
              className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-700 rounded-full transition-colors"
              disabled={isUploading}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Platform selection */}
          <div className="w-full mb-6">
            <p className="text-sm font-semibold text-slate-350 mb-3 text-left w-full">Buscar ofertas en:</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
              <label className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer select-none transition-all
                ${platforms.includes('computrabajo') ? 'border-primary bg-primary/10 text-white' : 'border-slate-700 bg-slate-800/20 hover:bg-slate-800/40 text-slate-400'}`}>
                <input 
                  type="checkbox" 
                  checked={platforms.includes('computrabajo')} 
                  onChange={() => handlePlatformChange('computrabajo')}
                  disabled={isUploading}
                  className="rounded border-slate-600 text-primary focus:ring-primary h-4 w-4 bg-slate-900"
                />
                <span className="font-semibold text-sm">Computrabajo</span>
              </label>

              <label className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer select-none transition-all
                ${platforms.includes('indeed') ? 'border-primary bg-primary/10 text-white' : 'border-slate-700 bg-slate-800/20 hover:bg-slate-800/40 text-slate-400'}`}>
                <input 
                  type="checkbox" 
                  checked={platforms.includes('indeed')} 
                  onChange={() => handlePlatformChange('indeed')}
                  disabled={isUploading}
                  className="rounded border-slate-600 text-primary focus:ring-primary h-4 w-4 bg-slate-900"
                />
                <span className="font-semibold text-sm">Indeed</span>
              </label>

              <label className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer select-none transition-all
                ${platforms.includes('linkedin') ? 'border-primary bg-primary/10 text-white' : 'border-slate-700 bg-slate-800/20 hover:bg-slate-800/40 text-slate-400'}`}>
                <input 
                  type="checkbox" 
                  checked={platforms.includes('linkedin')} 
                  onChange={() => handlePlatformChange('linkedin')}
                  disabled={isUploading}
                  className="rounded border-slate-600 text-primary focus:ring-primary h-4 w-4 bg-slate-900"
                />
                <span className="font-semibold text-sm">LinkedIn</span>
              </label>
            </div>
          </div>

          <button 
            onClick={handleUploadClick}
            disabled={isUploading}
            className={`primary-btn w-full py-3 text-lg flex items-center justify-center gap-2 ${isUploading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {isUploading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Iniciando análisis...
              </>
            ) : (
              '🚀 Analizar CV'
            )}
          </button>
        </div>
      )}
    </div>
  )
}
