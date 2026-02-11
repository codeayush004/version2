import { useState } from "react"
import { BrowserRouter, Routes, Route, Link } from "react-router-dom"
import Dashboard from "./components/Dashboard"
import ReviewPage from "./components/ReviewPage"
import Notification, { type Toast } from "./components/Notification"

export default function App() {
  const [loading, setLoading] = useState(false)
  const [toasts, setToasts] = useState<Toast[]>([])
  const [githubToken, setGithubToken] = useState<string | null>(localStorage.getItem("gh_token"))

  const notify = (type: Toast['type'], message: string, link?: Toast['link']) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts(prev => [...prev as Toast[], { id, type, message, link }])
  }

  const dismissToast = (id: string) => {
    setToasts(prev => (prev as Toast[]).filter(t => t.id !== id))
  }

  return (
    <BrowserRouter>
      <div className="relative min-h-screen overflow-x-hidden pt-10 px-6 sm:px-10 lg:px-16 selection:bg-indigo-500/30">
        <Notification toasts={toasts} onDismiss={dismissToast} />
        <div className="glow-mesh" />

        {/* Premium Navigation */}
        <nav className="max-w-7xl mx-auto mb-16 flex items-center justify-between p-4 glass-card border-white/10 sticky top-10 z-50 animate-in fade-in slide-in-from-top-4 duration-700">
          <Link to="/" className="flex items-center gap-4 group cursor-pointer decoration-none">
            <div className="w-12 h-12 rounded-2xl premium-gradient flex items-center justify-center p-0.5 shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-all duration-500 animate-float">
              <div className="w-full h-full bg-black rounded-[14px] flex items-center justify-center">
                <span className="text-2xl font-black text-white">D</span>
              </div>
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-tight text-white group-hover:text-glow transition-all">
                Docker <span className="text-zinc-500 font-light">Optimizer</span>
              </h1>
              <div className="text-[10px] text-zinc-500 uppercase tracking-widest font-black flex items-center gap-1.5 mt-0.5">
                <span className="w-1 h-1 rounded-full bg-indigo-500 animate-pulse" /> Analysis Engine
              </div>
            </div>
          </Link>

          <div className="flex items-center gap-4">
            <div className="h-8 w-[1px] bg-zinc-800" />
            <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest hidden sm:block">
              v1.1.0-interactive
            </span>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto pb-24">
          <Routes>
            <Route
              path="/"
              element={
                <Dashboard
                  notify={notify}
                  setLoading={setLoading}
                  githubToken={githubToken}
                  setGithubToken={(token) => {
                    setGithubToken(token);
                    if (token) localStorage.setItem("gh_token", token);
                    else localStorage.removeItem("gh_token");
                  }}
                />
              }
            />
            <Route
              path="/review/:id"
              element={<ReviewPage notify={notify} />}
            />
          </Routes>

          {loading && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] flex items-center justify-center animate-in fade-in duration-500">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-6 shadow-xl shadow-indigo-600/20"></div>
                <p className="text-2xl font-black text-white tracking-tight animate-pulse text-glow">
                  Optimizing Infrastructure Architecture...
                </p>
                <p className="text-zinc-500 mt-2 font-medium">Extracting performance optimizations</p>
              </div>
            </div>
          )}
        </main>

        <footer className="max-w-7xl mx-auto py-12 border-t border-zinc-900 flex justify-between items-center opacity-50 text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-600">
          <div className="flex gap-8">
            <a href="#" className="hover:text-zinc-400 transition-colors">Documentation</a>
            <a href="#" className="hover:text-zinc-400 transition-colors">Privacy</a>
            <a href="#" className="hover:text-zinc-400 transition-colors">Enterprise</a>
          </div>
          <span className="text-zinc-800">DCO_PLATFORM_V1.1</span>
        </footer>
      </div>
    </BrowserRouter>
  )
}
