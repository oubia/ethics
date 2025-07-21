import React, { useState, useEffect, useRef } from 'react';
const SourceFilesPanel = ({ sourceFiles, onClose }) => (
  <div className="glass-card md:h-[44rem] flex flex-col relative transition-all w-72 md:w-[22rem] opacity-100 mt-6">
    <div className="px-4 pt-2 pb-2 flex items-center justify-between">
      <h2 className="text-md font-bold text-[#6366f1]">(Files)</h2>
      <button onClick={onClose} className="text-[#6366f1] hover:underline">Chiudi</button>
    </div>
    <div className="flex-1 px-4 py-2 overflow-auto max-h-[36rem] min-h-[10rem]">
        {sourceFiles.length === 0 ? (
            <div className="text-gray-400 italic">Nessun file recuperato.</div>
        ) : (
            <ul className="list-disc ml-4 space-y-1">
            {sourceFiles.map((f, i) => (
                <li key={i} className="break-all text-sm text-gray-700">{f}</li>
            ))}
            </ul>
        )}
    </div>

  </div>
);

export default SourceFilesPanel;