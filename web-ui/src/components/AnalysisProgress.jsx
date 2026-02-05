import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

const AnalysisProgress = ({ taskId, onComplete, onError }) => {
    const [status, setStatus] = useState('pending');
    // Fake progress simulation since backend is 0 or 100 rn
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        let interval;
        const poll = async () => {
            try {
                const res = await axios.get(`/api/status/${taskId}`);
                const s = res.data.status;
                setStatus(s);

                if (s === 'completed') {
                    setProgress(100);
                    clearInterval(interval);
                    // Fetch result data
                    const resData = await axios.get(`/api/results/${taskId}`);
                    setTimeout(() => onComplete(resData.data), 500); // Small delay for UX
                } else if (s === 'failed') {
                    clearInterval(interval);
                    onError(res.data.error || "Unknown error");
                } else {
                    // Simulate progress if processing
                    setProgress(old => Math.min(old + 1, 90));
                }
            } catch (err) {
                console.error(err);
            }
        };

        interval = setInterval(poll, 1000); // Poll every 1s
        return () => clearInterval(interval);
    }, [taskId]);

    return (
        <div className="text-center animate-in fade-in duration-700">
            <div className="relative w-24 h-24 mx-auto mb-8">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <path
                        className="text-zinc-800"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="3"
                    />
                    <path
                        className="text-neon-green transition-all duration-300 ease-linear"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="3"
                        strokeDasharray={`${progress}, 100`}
                    />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-bold font-mono">{Math.floor(progress)}%</span>
                </div>
            </div>

            <h2 className="text-2xl font-bold mb-2">Analyzing Match</h2>
            <p className="text-zinc-500 animate-pulse">Detecting players, tracking movements, and generating insights...</p>

            <div className="mt-8 flex justify-center gap-2 text-xs text-zinc-600 font-mono">
                <span>ID: {taskId.slice(0, 8)}</span>
            </div>
        </div>
    );
};

export default AnalysisProgress;
