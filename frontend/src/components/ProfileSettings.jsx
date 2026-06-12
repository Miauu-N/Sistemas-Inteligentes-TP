import { useState, useEffect } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { User, Mail, Bell, Shield, LogOut, Check, Loader2 } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ProfileSettings({ isOpen, onClose }) {
  const { user, logout, getAccessTokenSilently } = useAuth0()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)
  const [successMsg, setSuccessMsg] = useState('')

  useEffect(() => {
    if (isOpen && user) {
      fetchPreferences()
    }
  }, [isOpen, user])

  const fetchPreferences = async () => {
    setLoading(true)
    try {
      const token = await getAccessTokenSilently()
      const response = await fetch(`${API_URL}/api/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setNotificationsEnabled(data.email_notifications_enabled)
      }
    } catch (error) {
      console.error('Error fetching preferences:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async () => {
    setSaving(true)
    setSuccessMsg('')
    try {
      const token = await getAccessTokenSilently()
      const newValue = !notificationsEnabled
      const response = await fetch(`${API_URL}/api/users/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ email_notifications_enabled: newValue })
      })

      if (response.ok) {
        setNotificationsEnabled(newValue)
        setSuccessMsg('Preferencias guardadas')
        setTimeout(() => setSuccessMsg(''), 3000)
      }
    } catch (error) {
      console.error('Error updating preferences:', error)
    } finally {
      setSaving(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
      <div 
        className="w-full max-w-md bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden glass-card transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative p-6 border-b border-slate-850 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <User className="w-5 h-5 text-blue-400" /> Perfil y Preferencias
          </h2>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-white transition-colors text-sm"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
              <p className="text-slate-400 text-sm">Cargando perfil...</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* User details */}
              <div className="flex items-center gap-4 bg-slate-950/50 p-4 rounded-xl border border-slate-800/40">
                {user?.picture ? (
                  <img 
                    src={user.picture} 
                    alt={user.name} 
                    className="w-14 h-14 rounded-full border border-blue-500/20"
                  />
                ) : (
                  <div className="w-14 h-14 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/20">
                    <User className="w-7 h-7 text-blue-400" />
                  </div>
                )}
                <div className="overflow-hidden">
                  <h3 className="font-bold text-white text-base truncate">{user?.name || user?.nickname}</h3>
                  <p className="text-slate-400 text-sm flex items-center gap-1.5 truncate mt-0.5">
                    <Mail className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    {user?.email || 'Sin correo asociado'}
                  </p>
                </div>
              </div>

              {/* Notification preferences */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Bell className="w-3.5 h-3.5" /> Suscripciones
                </h4>
                
                <div className="flex items-center justify-between bg-slate-950/30 p-4 rounded-xl border border-slate-800/20">
                  <div>
                    <p className="text-sm font-semibold text-white">Recomendaciones Semanales</p>
                    <p className="text-xs text-slate-400 mt-1 max-w-[240px]">
                      Recibir correos los lunes con las mejores vacantes basadas en tu perfil.
                    </p>
                  </div>
                  
                  {/* Switch component */}
                  <button
                    onClick={handleToggle}
                    disabled={saving}
                    className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      notificationsEnabled ? 'bg-blue-600' : 'bg-slate-700'
                    } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span
                      className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                        notificationsEnabled ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Status messages */}
              {successMsg && (
                <div className="flex items-center gap-1.5 text-green-400 text-xs bg-green-500/10 border border-green-500/20 px-3 py-2 rounded-lg justify-center animate-fade-in">
                  <Check className="w-3.5 h-3.5" /> {successMsg}
                </div>
              )}

              {/* Security info / Logout */}
              <div className="pt-4 border-t border-slate-850 flex items-center justify-between gap-4">
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Conexión segura
                </span>
                
                <button
                  onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                  className="flex items-center gap-1.5 text-sm text-red-400 hover:text-red-300 font-semibold transition-colors py-1.5 px-3 rounded-lg hover:bg-red-500/10"
                >
                  <LogOut className="w-4 h-4" /> Cerrar sesión
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
