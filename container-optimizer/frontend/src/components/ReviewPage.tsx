import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import axios from "axios"

export default function ReviewPage({ notify }: { notify: (type: 'success' | 'error' | 'info', message: string, link?: { label: string, url: string }) => void }) {
    const { id } = useParams<{ id: string }>()
    const [data, setData] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [approving, setApproving] = useState(false)
    const [prLink, setPrLink] = useState<string | null>(null)

    useEffect(() => {
        const fetchConsent = async () => {
            try {
                const res = await axios.get(`http://127.0.0.1:8000/api/consent/${id}`)
                setData(res.data)
            } catch (err) {
                console.error("Failed to fetch consent data", err)
                notify("error", "Failed to load review data. The link might be expired.")
            } finally {
                setLoading(false)
            }
        }
        fetchConsent()
    }, [id])

    const handleApprove = async () => {
        setApproving(true)
        try {
            const res = await axios.post(`http://127.0.0.1:8000/api/consent/${id}/approve`)
            setPrLink(res.data.pr_link)
            notify("success", "Optimization Approved! Pull Request Created.")
        } catch (err: any) {
            console.error("Approval failed", err)
            notify("error", `Approval failed: ${err.response?.data?.detail || err.message}`)
        } finally {
            setApproving(false)
        }
    }

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-zinc-500 font-bold uppercase tracking-widest text-xs">Fetching Optimization Details...</p>
            </div>
        )
    }

    if (!data) return null

    return (
        <div className="animate-in fade-in duration-700">
            <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <span className="px-3 py-1 bg-indigo-600/20 border border-indigo-500/30 rounded-full text-[10px] font-black text-indigo-400 uppercase tracking-widest">
                            Optimization Review
                        </span>
                        <span className="text-zinc-600 text-[10px] font-bold">ID: {id}</span>
                    </div>
                    <h2 className="text-4xl font-black text-white tracking-tight">Approve Improvements</h2>
                    <p className="text-zinc-500 mt-2 font-medium">
                        Review the suggested changes for <span className="text-zinc-300 font-bold">{data.url}</span> ({data.path})
                    </p>
                </div>

                {!prLink ? (
                    <button
                        onClick={handleApprove}
                        disabled={approving}
                        className="px-10 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-black transition-all shadow-2xl shadow-indigo-600/20 active:scale-95 disabled:opacity-50 flex items-center gap-3"
                    >
                        {approving ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                APPROVING...
                            </>
                        ) : (
                            <>
                                <span>APPROVE & CREATE PR</span>
                                <span className="text-indigo-300">🚀</span>
                            </>
                        )}
                    </button>
                ) : (
                    <a
                        href={prLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-10 py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-2xl font-black transition-all shadow-2xl shadow-emerald-600/20 flex items-center gap-3 animate-bounce"
                    >
                        <span>VIEW PULL REQUEST</span>
                        <span>↗️</span>
                    </a>
                )}
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-4">
                    <div className="flex items-center justify-between px-2">
                        <h3 className="text-sm font-black text-zinc-500 uppercase tracking-widest">Original Dockerfile</h3>
                        <span className="text-[10px] bg-red-500/10 text-red-500 px-2 py-0.5 rounded border border-red-500/20 font-bold uppercase">Legacy</span>
                    </div>
                    <div className="glass-card overflow-hidden border-white/5">
                        <pre className="p-6 text-[11px] font-mono text-zinc-500 leading-relaxed overflow-auto max-h-[600px] bg-black/20">
                            {data.original_content}
                        </pre>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center justify-between px-2">
                        <h3 className="text-sm font-black text-indigo-400 uppercase tracking-widest">Optimized Version</h3>
                        <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20 font-bold uppercase flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" /> Recommended
                        </span>
                    </div>
                    <div className="relative group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
                        <div className="relative glass-card overflow-hidden border-indigo-500/30 shadow-2xl shadow-indigo-500/5">
                            <pre className="p-6 text-[11px] font-mono text-zinc-200 leading-relaxed overflow-auto max-h-[600px] bg-indigo-950/10">
                                {data.optimized_content}
                            </pre>
                        </div>
                    </div>
                </div>
            </div>

            {prLink && (
                <div className="mt-12 p-8 glass-card border-emerald-500/20 bg-emerald-500/5 animate-in slide-in-from-bottom-4 duration-1000">
                    <div className="flex items-center gap-6">
                        <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center text-3xl">🎉</div>
                        <div>
                            <h3 className="text-2xl font-black text-white">Pull Request Dispatched!</h3>
                            <p className="text-zinc-500 font-medium">Our Optimizer Bot has successfully forked and opened a PR on the target repository.</p>
                            <div className="mt-4 flex gap-4">
                                <a href={prLink} target="_blank" className="text-emerald-400 font-bold hover:underline">Click here to view the PR on GitHub</a>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
