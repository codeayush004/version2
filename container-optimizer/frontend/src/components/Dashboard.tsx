import { useState } from "react"
import ContainerTable from "./ContainerTable"
import ActionPanel from "./ActionPanel"
import ResultViewer from "./ResultViewer"
import DockerfileUpload from "./DockerfileUpload"
import GitHubScanner from "./GitHubScanner"
import DockerHubScanner from "./DockerHubScanner"
import type { Container } from "../types"

interface DashboardProps {
    notify: (type: 'success' | 'error' | 'info', message: string, link?: { label: string, url: string }) => void
    setLoading: (loading: boolean) => void
    githubToken: string | null
    setGithubToken: (token: string | null) => void
}

export default function Dashboard({ notify, setLoading, githubToken, setGithubToken }: DashboardProps) {
    const [selected, setSelected] = useState<Container | null>(null)
    const [result, setResult] = useState<any>(null)
    const [view, setView] = useState<"runtime" | "static" | "github" | "registry">("runtime")

    const handleViewChange = (newView: "runtime" | "static" | "github" | "registry") => {
        setView(newView)
        setResult(null)
        setSelected(null)
        setLoading(false)
    }

    return (
        <>
            <div className="hidden md:flex items-center bg-black/40 p-1.5 rounded-2xl border border-white/5 space-x-1 w-fit mx-auto mb-12">
                {(["runtime", "static", "github", "registry"] as const).map((v) => (
                    <button
                        key={v}
                        onClick={() => handleViewChange(v)}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all duration-500 ${view === v
                            ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20"
                            : "text-zinc-500 hover:text-zinc-200 hover:bg-white/5"
                            }`}
                    >
                        {v === "static" ? "Static" : v === "github" ? "GitHub" : v === "registry" ? "Registry" : "Runtime"}
                    </button>
                ))}
            </div>

            {view === "runtime" ? (
                <section className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
                        <div className="relative glass-card p-10">
                            <header className="mb-10 flex items-center justify-between">
                                <div>
                                    <h2 className="text-3xl font-black text-white mb-2">Fleet Management</h2>
                                    <p className="text-zinc-500 text-sm font-medium">Analyze and optimize containers currently running in your ecosystem.</p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="px-4 py-1.5 rounded-full bg-zinc-950 border border-zinc-800 text-[10px] font-black uppercase text-zinc-500 tracking-tighter">Live Monitor</span>
                                </div>
                            </header>
                            <ContainerTable onSelect={setSelected} />
                        </div>
                    </div>

                    <ActionPanel
                        container={selected}
                        onResult={setResult}
                        setLoading={setLoading}
                        notify={notify}
                    />
                </section>
            ) : view === "static" ? (
                <div className="animate-in fade-in zoom-in-95 duration-1000">
                    <DockerfileUpload onResult={setResult} setLoading={setLoading} notify={notify} />
                </div>
            ) : view === "github" ? (
                <div className="animate-in fade-in slide-in-from-right-8 duration-1000">
                    <GitHubScanner
                        onResult={setResult}
                        setLoading={setLoading}
                        notify={notify}
                        githubToken={githubToken}
                        setGithubToken={setGithubToken}
                    />
                </div>
            ) : (
                <div className="animate-in fade-in slide-in-from-left-8 duration-1000">
                    <DockerHubScanner onResult={setResult} setLoading={setLoading} notify={notify} />
                </div>
            )}

            <div className="mt-20">
                <ResultViewer result={result} notify={notify} />
            </div>
        </>
    )
}
