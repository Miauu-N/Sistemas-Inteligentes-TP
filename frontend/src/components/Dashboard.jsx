import { Download, RotateCcw, Target, Briefcase, AlertCircle, Lightbulb, CheckCircle2 } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Dashboard({ data, jobId, onReset }) {
  const { 
    cv_summary, 
    matching_score, 
    executive_summary, 
    gaps, 
    recommendations, 
    market_overview,
    strengths,
    total_jobs_analyzed,
    job_listings
  } = data

  const scorePercentage = Math.round((matching_score || 0) * 100)

  const handleDownload = () => {
    window.open(`${API_URL}/api/report/${jobId}/pdf`, '_blank')
  }

  return (
    <div className="w-full flex flex-col gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-4">
        <button onClick={onReset} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
          <RotateCcw className="w-4 h-4" /> Nuevo análisis
        </button>
        <button onClick={handleDownload} className="primary-btn flex items-center gap-2">
          <Download className="w-4 h-4" /> Descargar PDF
        </button>
      </div>

      {/* Demo Mode / Mock Warning Banner */}
      {job_listings?.some(job => job.is_mock) && (
        <div className="glass-card p-5 border-l-4 border-l-amber-500 bg-amber-500/10 text-amber-250 flex items-start gap-3 w-full animate-in fade-in slide-in-from-top-4 duration-500">
          <AlertCircle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5 animate-pulse" />
          <div>
            <h4 className="font-bold text-amber-300 text-lg">Modo Demo (Datos de Respaldo)</h4>
            <p className="text-sm text-slate-350 leading-relaxed mt-1">
              Las consultas en tiempo real a los portales seleccionados fallaron o fueron bloqueadas por protecciones anti-bot (ej. Cloudflare/Captcha). 
              Para poder completar el análisis de tu perfil, el sistema cargó ofertas de referencia simuladas.
            </p>
          </div>
        </div>
      )}

      {/* Summary Section */}
      <div className="glass-card p-6 md:p-8 border-l-4 border-l-primary">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Target className="text-primary" /> Resumen Ejecutivo
        </h2>
        <p className="text-lg text-slate-300 leading-relaxed">{executive_summary}</p>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard title="Score de Match" value={`${scorePercentage}%`} icon={<Target />} color="text-green-400" />
        <MetricCard title="Ofertas Analizadas" value={total_jobs_analyzed} icon={<Briefcase />} color="text-blue-400" />
        <MetricCard title="Brechas Encontradas" value={gaps?.length || 0} icon={<AlertCircle />} color="text-orange-400" />
        <MetricCard title="Recomendaciones" value={recommendations?.length || 0} icon={<Lightbulb />} color="text-yellow-400" />
      </div>

      {/* Profile & Skills Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="glass-card p-6">
          <h3 className="text-xl font-bold mb-4 border-b border-slate-700 pb-2">Perfil del CV</h3>
          <ul className="space-y-3 text-slate-300">
            <li><span className="font-semibold text-slate-400">Nombre:</span> {cv_summary?.name}</li>
            <li><span className="font-semibold text-slate-400">Seniority:</span> {cv_summary?.seniority}</li>
            <li><span className="font-semibold text-slate-400">Ubicación:</span> {cv_summary?.location}</li>
          </ul>
          
          <h4 className="font-bold mt-6 mb-3 text-slate-400">Tecnologías Detectadas</h4>
          <div className="flex flex-wrap gap-2">
            {cv_summary?.technologies?.map(tech => (
              <span key={tech} className="px-3 py-1 bg-slate-800 border border-slate-600 rounded-full text-sm">
                {tech}
              </span>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-xl font-bold mb-4 border-b border-slate-700 pb-2 flex items-center gap-2">
            <CheckCircle2 className="text-green-400" /> Fortalezas
          </h3>
          <ul className="space-y-3">
            {strengths?.map((strength, i) => (
              <li key={i} className="flex items-start gap-3 bg-green-500/10 border border-green-500/20 p-3 rounded-lg text-green-100">
                <span className="text-green-400 mt-1">•</span> {strength}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Gaps & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Gaps */}
        <div className="glass-card p-6 border-t-4 border-t-orange-500">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <AlertCircle className="text-orange-400" /> Brechas Detectadas
          </h3>
          <div className="space-y-4">
            {gaps?.map((gap, i) => {
              const priority = gap.priority || 'media'
              const priorityClass = priority.toLowerCase() === 'alta' ? 'text-red-400' : 'text-slate-400'
              return (
                <div key={i} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                  <h4 className="font-bold text-orange-300 mb-2">{gap.skill_or_requirement}</h4>
                  <p className="text-sm text-slate-300">{gap.description}</p>
                  <div className="mt-3 flex justify-between items-center text-xs">
                    <span className={`px-2 py-1 rounded bg-slate-700 ${priorityClass}`}>
                      Prioridad: {priority.toUpperCase()}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Recommendations */}
        <div className="glass-card p-6 border-t-4 border-t-primary">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <Lightbulb className="text-yellow-400" /> Plan de Acción
          </h3>
          <div className="space-y-4">
            {recommendations?.map((rec, i) => (
              <div key={i} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                <h4 className="font-bold text-blue-300 mb-2">{rec.title}</h4>
                <p className="text-sm text-slate-300 mb-3">{rec.description}</p>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="px-2 py-1 rounded bg-slate-700 text-slate-300">
                    ⏱️ {rec.estimated_time}
                  </span>
                  <span className="px-2 py-1 rounded bg-slate-700 text-purple-300">
                    🏷️ {rec.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
      </div>

      {/* Reference Job Listings */}
      {job_listings && job_listings.length > 0 && (
        <details className="glass-card p-6 border-t-4 border-t-blue-500 group [&_summary::-webkit-details-marker]:hidden" open={false}>
          <summary className="flex justify-between items-center font-bold text-xl cursor-pointer select-none">
            <span className="flex items-center gap-2">
              <Briefcase className="text-blue-400" /> Ofertas de Referencia Encontradas ({job_listings.length})
            </span>
            <span className="text-slate-400 transition-transform duration-300 group-open:rotate-180">
              <svg fill="none" height="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="20"><path d="M6 9l6 6 6-6"></path></svg>
            </span>
          </summary>
          <div className="mt-6 space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
            <p className="text-slate-400 text-sm mb-4">
              Se analizaron las siguientes ofertas laborales para estructurar este reporte de empleabilidad:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {job_listings.map((job, idx) => {
                const title = job.title || 'Oferta de empleo'
                const company = job.company || 'Empresa'
                const location = job.location || ''
                const modality = job.modality || ''
                const url = job.source_url || job.url || ''
                const platform = job.source_platform || 'portal'

                return (
                  <div key={idx} className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/60 flex flex-col justify-between hover:border-slate-500 transition-colors">
                    <div>
                      <div className="flex justify-between items-start gap-2 mb-2">
                        <h4 className="font-bold text-slate-100 line-clamp-1" title={title}>{title}</h4>
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          {platform}
                        </span>
                      </div>
                      <p className="text-sm font-semibold text-slate-300 mb-1">{company}</p>
                      <div className="flex gap-2 text-xs text-slate-400 mb-4">
                        {location && <span>📍 {location}</span>}
                        {modality && <span>💼 {modality}</span>}
                      </div>
                    </div>
                    {url && url.startsWith('http') && (
                      <a 
                        href={url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-xs font-semibold text-primary hover:text-blue-400 flex items-center gap-1 mt-auto self-start"
                      >
                        Ver oferta original ↗
                      </a>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </details>
      )}
    </div>
  )
}

function MetricCard({ title, value, icon, color }) {
  return (
    <div className="glass-card p-6 flex flex-col items-center justify-center text-center">
      <div className={`${color} mb-2 w-8 h-8 flex items-center justify-center`}>
        {icon}
      </div>
      <h4 className="text-3xl font-black mb-1">{value}</h4>
      <p className="text-slate-400 text-sm font-medium">{title}</p>
    </div>
  )
}
