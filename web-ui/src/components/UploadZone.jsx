import React, { useRef, useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileVideo, Loader2 } from 'lucide-react';

const UploadZone = ({ onUploadStart }) => {
    const fileInputRef = useRef(null);
    const [isDragOver, setIsDragOver] = useState(false);
    const [isUploading, setIsUploading] = useState(false);

    const handleFile = async (file) => {
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            // In dev, vite proxy handles /api -> http://localhost:8000
            // But we set proxy rewrite /api in vite.config
            const res = await axios.post('/api/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            onUploadStart(res.data.task_id);
        } catch (err) {
            console.error(err);
            alert("Upload failed.");
            setIsUploading(false);
        }
    };

    const onDrop = (e) => {
        e.preventDefault();
        setIsDragOver(false);
        handleFile(e.dataTransfer.files[0]);
    };

    return (
        <div className="w-full max-w-xl animate-in fade-in zoom-in duration-500">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-500 mb-2">Upload Match Video</h2>
                <p className="text-zinc-400">AI-powered analysis of your gameplay mechanics and strategy.</p>
            </div>

            <div
                className={`
          relative group cursor-pointer
          border-2 border-dashed rounded-3xl p-12 transition-all duration-300 ease-out
          flex flex-col items-center justify-center gap-4
          ${isDragOver ? 'border-neon-green bg-neon-green/5 scale-[1.02]' : 'border-zinc-800 bg-zinc-900/50 hover:border-zinc-600 hover:bg-zinc-900'}
        `}
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={onDrop}
                onClick={() => !isUploading && fileInputRef.current.click()}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept="video/mp4,video/mov,video/avi"
                    onChange={(e) => handleFile(e.target.files[0])}
                />

                <div className={`p-4 rounded-full bg-zinc-800 group-hover:bg-zinc-700 transition-colors ${isUploading ? 'animate-pulse' : ''}`}>
                    {isUploading ? <Loader2 className="w-8 h-8 text-neon-green animate-spin" /> : <UploadCloud className="w-8 h-8 text-zinc-300 group-hover:text-white" />}
                </div>

                <div className="text-center">
                    <p className="font-medium text-lg text-zinc-200">
                        {isUploading ? "Uploading & Initializing..." : "Click to upload or drag and drop"}
                    </p>
                    <p className="text-sm text-zinc-500 mt-1">MP4, MOV (Max 100MB recom.)</p>
                </div>
            </div>
        </div>
    );
};

export default UploadZone;
