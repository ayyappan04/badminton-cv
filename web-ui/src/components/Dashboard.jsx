import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Play, Download, RefreshCw, ChevronRight } from 'lucide-react';

const Dashboard = ({ taskId, data, onReset }) => {
    return (
        <div className="w-full h-full flex flex-col gap-6 animate-in slide-in-from-bottom-10 duration-700">
            {/* Top Bar */}
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold text-white">Match Report</h2>
                    <p className="text-zinc-400">Analysis completed successfully.</p>
                </div>
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-800 hover:bg-zinc-700 transition text-sm font-medium"
                >
                    <RefreshCw className="w-4 h-4" /> Analyze Another
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[70vh]">
                {/* Left: Video Player */}
                <div className="lg:col-span-2 bg-black rounded-3xl border border-zinc-800 overflow-hidden flex flex-col relative group">
                    <video
                        src={`/api/video/${taskId}`}
                        controls
                        className="w-full h-full object-contain bg-black"
                        poster="https://via.placeholder.com/1280x720/111/333?text=Deep+Analysis"
                    />
                    <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded-full text-xs font-mono border border-neon-green/30 text-neon-green">
                        AI OVERLAY ACTIVE
                    </div>
                </div>

                {/* Right: Report */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-6 overflow-y-auto custom-scrollbar">
                    <article className="prose prose-invert prose-headings:text-white prose-a:text-neon-green prose-strong:text-white prose-sm max-w-none">
                        <ReactMarkdown>{data?.report_markdown || "**Error loading report.**"}</ReactMarkdown>
                    </article>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
