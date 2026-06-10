import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'

export default function ProgressTracker({ message }) {
  const [progress, setProgress] = useState(0)

  // Mapeo simple para simular progreso basado en el mensaje recibido
  useEffect(() => {
    if (!message) return
    
    if (message.includes('Validando')) setProgress(10)
    else if (message.includes('estructurando')) setProgress(25)
    else if (message.includes('Buscando ofertas')) setProgress(50)
    else if (message.includes('Analizando tendencias')) setProgress(65)
    else if (message.includes('Detectando brechas')) setProgress(80)
    else if (message.includes('Recomendaciones')) setProgress(90)
    else if (message.includes('Construyendo')) setProgress(98)
  }, [message])

  return (
    <div className="glass-card p-8 md:p-12 w-full max-w-2xl flex flex-col items-center mt-8">
      <Loader2 className="w-16 h-16 text-primary animate-spin mb-6" />
      <h3 className="text-2xl font-bold text-slate-100 mb-2">Analizando CV</h3>
      <p className="text-lg text-slate-400 text-center mb-8 h-8 transition-all">
        {message || 'Iniciando proceso...'}
      </p>
      
      <div className="w-full bg-slate-800 rounded-full h-3 mb-2 overflow-hidden border border-slate-700">
        <div 
          className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-right w-full text-sm font-medium text-slate-500">{progress}% completado</p>
    </div>
  )
}
