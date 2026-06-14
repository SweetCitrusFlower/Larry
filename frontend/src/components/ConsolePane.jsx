import React from 'react';

const ConsolePane = ({ output, input, setInput }) => {
  return (
    <div className="flex flex-col h-full bg-slate-950 font-mono text-sm w-full">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800 text-xs font-semibold text-slate-400">
        <div className="flex gap-4">
          <span className="cursor-pointer text-blue-400 border-b border-blue-400 pb-1">Output</span>
          <span className="cursor-pointer hover:text-slate-200 pb-1">Terminal</span>
        </div>
        <button className="cursor-pointer hover:text-slate-200 transition-colors">Clear</button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        <pre className="whitespace-pre-wrap text-slate-300 font-mono text-[13px] leading-relaxed">
          {output || '> Waiting for execution...'}
        </pre>
      </div>
      <div className="flex items-center gap-2 px-4 py-3 bg-slate-900/50 border-t border-slate-800">
        <span className="text-emerald-400 font-bold">$</span>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a command..."
          className="flex-1 bg-transparent border-none outline-none text-slate-200 placeholder-slate-600 font-mono text-[13px]"
          spellCheck="false"
        />
      </div>
    </div>
  );
};

export default ConsolePane;
