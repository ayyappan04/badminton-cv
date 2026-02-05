import React, { useState } from 'react';
import UploadZone from './components/UploadZone';
import AnalysisProgress from './components/AnalysisProgress';
import Dashboard from './components/Dashboard';
import { Activity } from 'lucide-react';

function App() {
    const [currentView, setCurrentView] = useState('upload'); // upload, processing, result
    const [taskId, setTaskId] = useState(null);
    const [resultData, setResultData] = useState(null);

    return (
        <div className="min-h-screen bg-neutral-950 text-white flex flex-col font-sans selection:bg-neon-green selection:text-black">
            {/* Header */}
            <header className="border-b border-white/10 p-6 flex items-center justify-between backdrop-blur-md bg-black/20 sticky top-0 z-50">
                <div className="flex items-center gap-3">
                    <Activity className="text-neon-green w-6 h-6" />
                    <h1 className="text-xl font-bold tracking-tight">Badminton<span className="text-neon-green">AI</span> Analyst</h1>
                </div>
                <div className="text-xs font-mono text-zinc-500 uppercase tracking-widest">v1.0.0 Alpha</div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col items-center justify-center p-6 w-full max-w-7xl mx-auto">

                {currentView === 'upload' && (
                    <UploadZone
                        onUploadStart={(id) => {
                            setTaskId(id);
                            setCurrentView('processing');
                        }}
                    />
                )}

                {currentView === 'processing' && taskId && (
                    <AnalysisProgress
                        taskId={taskId}
                        onComplete={(data) => {
                            setResultData(data);
                            setCurrentView('result');
                        }}
                        onError={(err) => {
                            alert("Analysis failed: " + err);
                            setCurrentView('upload');
                        }}
                    />
                )}

                {currentView === 'result' && taskId && (
                    <Dashboard
                        taskId={taskId}
                        data={resultData}
                        onReset={() => {
                            setTaskId(null);
                            setResultData(null);
                            setCurrentView('upload');
                        }}
                    />
                )}

            </main>
        </div>
    );
}

export default App;
