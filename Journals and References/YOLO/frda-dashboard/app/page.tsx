'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  User, 
  Smartphone, 
  Camera, 
  Activity, 
  Lock, 
  Unlock, 
  Scan, 
  Eye, 
  Server, 
  CheckCircle, 
  XCircle,
  Terminal
} from 'lucide-react';

// --- Components ---

// 1. The "Live" Camera Feed Simulation
const CameraFeed = ({ scenario, scanLine, isScanning }: { scenario: string; scanLine: number; isScanning: boolean }) => {
  return (
    <div className="relative w-full h-96 bg-slate-900 rounded-xl overflow-hidden border-2 border-slate-700 shadow-2xl">
      {/* Header Overlay */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-2 bg-black/60 px-3 py-1 rounded text-xs text-cyan-400 font-mono">
        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
        REC • 1080p • YOLO11-n Inference
      </div>

      {/* The "Video" Content - Abstract Representation */}
      <div className="absolute inset-0 flex items-center justify-center">
        {scenario === 'normal' && (
          <div className="flex flex-col items-center opacity-80 transition-all duration-500">
            <User size={160} className="text-slate-400" />
            <div className="mt-4 text-slate-500 font-mono">Subject: 98.2% Match</div>
          </div>
        )}

        {scenario === 'spoof' && (
          <div className="flex flex-col items-center animate-pulse transition-all duration-500">
             <div className="relative">
               <div className="absolute -inset-4 border-4 border-red-500/50 rounded-lg animate-ping"></div>
               <div className="border-4 border-red-600 p-6 rounded-lg bg-slate-800/80">
                  <User size={140} className="text-red-400 blur-[2px]" />
                  <div className="absolute bottom-2 right-2 bg-red-600 text-white text-xs px-2 py-0.5 rounded">STATIC TEXTURE</div>
               </div>
             </div>
          </div>
        )}

        {scenario === 'device' && (
          <div className="flex flex-col items-center transition-all duration-500">
            <div className="relative">
              <User size={160} className="text-slate-500" />
              {/* The detected phone */}
              <div className="absolute bottom-0 -right-12 animate-bounce">
                 <div className="border-2 border-yellow-400 p-2 bg-yellow-900/30 rounded">
                    <Smartphone size={64} className="text-yellow-400" />
                    <div className="absolute -top-3 -right-3 bg-yellow-500 text-black text-xs font-bold px-1 rounded">OBJ: PHONE</div>
                 </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* YOLO Bounding Boxes Layer */}
      <div className="absolute inset-0 z-10">
         {scenario === 'normal' && (
           <div className="absolute top-1/4 left-1/3 w-1/3 h-1/2 border-2 border-green-500 rounded-lg opacity-80">
              <div className="absolute -top-6 left-0 bg-green-500 text-black text-xs px-2 py-1 font-bold">
                FACE_REAL: 0.99
              </div>
           </div>
         )}
         
         {scenario === 'spoof' && (
           <div className="absolute top-1/4 left-1/3 w-1/3 h-1/2 border-2 border-red-600 rounded-lg">
              <div className="absolute -top-6 left-0 bg-red-600 text-white text-xs px-2 py-1 font-bold flex items-center gap-1">
                <AlertTriangle size={10} /> SPOOF_PRINT: 0.98
              </div>
           </div>
         )}

         {scenario === 'device' && (
           <>
             <div className="absolute top-1/4 left-1/3 w-1/3 h-1/2 border-2 border-green-500/50 rounded-lg border-dashed"></div>
             <div className="absolute bottom-1/4 right-1/4 w-24 h-32 border-2 border-yellow-400 rounded">
                <div className="absolute -bottom-6 left-0 bg-yellow-400 text-black text-xs px-2 py-1 font-bold">
                  REC_DEVICE: 0.95
                </div>
             </div>
           </>
         )}
      </div>

      {/* Scanning Effect */}
      {isScanning && (
        <div 
          className="absolute inset-0 z-0 bg-gradient-to-b from-transparent via-cyan-500/20 to-transparent w-full h-2 pointer-events-none"
          style={{ top: `${scanLine}%` }}
        />
      )}
    </div>
  );
};

// 2. The SOC Agent Pipeline
const SOCPipeline = ({ activeAgent, logs }: { activeAgent: string | null; logs: Array<{ time: string; agent: string; message: string; color: string }> }) => {
  const agents = [
    { id: 'FRDA', label: 'FRDA', sub: 'Sensor Layer', icon: Eye, color: 'text-cyan-400', border: 'border-cyan-500' },
    { id: 'ADA', label: 'ADA', sub: 'Alert Dispatch', icon: Activity, color: 'text-blue-400', border: 'border-blue-500' },
    { id: 'TAA', label: 'TAA', sub: 'Threat Analysis', icon: Shield, color: 'text-purple-400', border: 'border-purple-500' },
    { id: 'CLA', label: 'CLA', sub: 'Response', icon: Lock, color: 'text-red-400', border: 'border-red-500' },
  ];

  return (
    <div className="mt-6 bg-slate-800 p-4 rounded-xl border border-slate-700">
      <h3 className="text-sm font-bold text-slate-400 mb-4 uppercase tracking-wider flex items-center gap-2">
        <Server size={16} /> SOC Multi-Agent Workflow
      </h3>
      
      {/* Flowchart */}
      <div className="flex justify-between items-center relative mb-6">
        {/* Connector Line */}
        <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-700 -z-0"></div>
        
        {agents.map((agent) => {
           const isActive = activeAgent === agent.id || logs.some(l => l.agent === agent.id);
           const IconComponent = agent.icon;
           return (
            <div key={agent.id} className={`relative z-10 flex flex-col items-center bg-slate-900 p-3 rounded-lg border-2 transition-all duration-300 ${isActive ? agent.border + ' scale-110 shadow-lg' : 'border-slate-700 opacity-50'}`}>
              <IconComponent className={`mb-1 ${isActive ? agent.color : 'text-slate-600'}`} size={20} />
              <span className={`font-bold text-xs ${isActive ? 'text-white' : 'text-slate-600'}`}>{agent.label}</span>
              <span className="text-[10px] text-slate-500">{agent.sub}</span>
            </div>
           );
        })}
      </div>

      {/* Terminal Logs */}
      <div className="bg-black rounded p-3 h-32 overflow-y-auto font-mono text-xs border border-slate-700">
        {logs.length === 0 ? (
          <span className="text-slate-600 animate-pulse">_waiting for telemetry...</span>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="mb-1 border-l-2 border-slate-700 pl-2">
              <span className="text-slate-500">[{log.time}]</span>{' '}
              <span className={`${log.color} font-bold`}>{log.agent}:</span>{' '}
              <span className="text-slate-300">{log.message}</span>
            </div>
          ))
        )}
        <div id="log-end" />
      </div>
    </div>
  );
};

// 3. Threat Vector Gauges
const ThreatVectorPanel = ({ riskScore, vectorType }: { riskScore: number; vectorType: string }) => {
  // Calculate color based on risk score
  let scoreColor = 'text-green-500';
  let barColor = 'bg-green-500';
  let status = 'LOW RISK';
  
  if (riskScore > 40 && riskScore < 80) {
    scoreColor = 'text-yellow-500';
    barColor = 'bg-yellow-500';
    status = 'ELEVATED';
  } else if (riskScore >= 80) {
    scoreColor = 'text-red-500';
    barColor = 'bg-red-500';
    status = 'CRITICAL';
  }

  return (
    <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 h-full">
      <h3 className="text-sm font-bold text-slate-400 mb-4 uppercase tracking-wider flex items-center gap-2">
        <Activity size={16} /> Threat Vector Analysis
      </h3>

      <div className="flex flex-col gap-6">
        {/* Main Score */}
        <div className="text-center p-4 bg-slate-900 rounded-lg border border-slate-700">
          <div className="text-slate-500 text-xs mb-1">AGGREGATED RISK SCORE</div>
          <div className={`text-5xl font-black ${scoreColor} font-mono`}>{riskScore}/100</div>
          <div className={`text-xs font-bold mt-2 px-2 py-1 rounded ${barColor} text-black inline-block`}>
            STATUS: {status}
          </div>
        </div>

        {/* Vector Breakdown */}
        <div className="space-y-3">
           <div className="flex justify-between text-xs text-slate-400">
             <span>Spoofing Probability</span>
             <span className={vectorType === 'spoof' ? 'text-red-400 font-bold' : ''}>
               {vectorType === 'spoof' ? '98%' : '2%'}
             </span>
           </div>
           <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
             <div 
               className={`h-full transition-all duration-1000 ${vectorType === 'spoof' ? 'bg-red-500 w-[98%]' : 'bg-blue-500 w-[2%]'}`} 
             />
           </div>

           <div className="flex justify-between text-xs text-slate-400">
             <span>Device Detection</span>
             <span className={vectorType === 'device' ? 'text-yellow-400 font-bold' : ''}>
               {vectorType === 'device' ? 'DETECTED' : 'NONE'}
             </span>
           </div>
           <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
             <div 
               className={`h-full transition-all duration-1000 ${vectorType === 'device' ? 'bg-yellow-500 w-[95%]' : 'bg-blue-500 w-[0%]'}`} 
             />
           </div>
           
           <div className="flex justify-between text-xs text-slate-400">
             <span>Behavioral Anomaly</span>
             <span className={vectorType !== 'normal' ? 'text-orange-400' : ''}>
               {vectorType !== 'normal' ? 'HIGH' : 'LOW'}
             </span>
           </div>
           <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
              <div 
               className={`h-full transition-all duration-1000 ${vectorType !== 'normal' ? 'bg-orange-500 w-[70%]' : 'bg-blue-500 w-[12%]'}`} 
             />
           </div>
        </div>
        
        {/* Final Decision Box */}
        <div className={`mt-4 p-3 rounded border ${riskScore >= 80 ? 'bg-red-900/20 border-red-500/50' : 'bg-green-900/20 border-green-500/50'} flex items-center justify-center gap-3`}>
           {riskScore >= 80 ? <Lock className="text-red-500" /> : <Unlock className="text-green-500" />}
           <div className="text-center">
             <div className="text-[10px] text-slate-400 uppercase">System Action</div>
             <div className={`font-bold ${riskScore >= 80 ? 'text-red-400' : 'text-green-400'}`}>
               {riskScore >= 80 ? 'BLOCK TRANSACTION' : 'ALLOW ACCESS'}
             </div>
           </div>
        </div>

      </div>
    </div>
  );
};

// --- Main App Container ---

export default function FRDASimulation() {
  const [scenario, setScenario] = useState('normal'); // normal, spoof, device
  const [riskScore, setRiskScore] = useState(12);
  const [scanLine, setScanLine] = useState(0);
  const [logs, setLogs] = useState<Array<{ time: string; agent: string; message: string; color: string }>>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);

  // Animation Loop for scan line
  useEffect(() => {
    const interval = setInterval(() => {
      setScanLine(prev => (prev + 2) % 100);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Helper to add logs with delay
  const addLog = (agent: string, message: string, color: string, delay: number) => {
    setTimeout(() => {
      setActiveAgent(agent);
      setLogs(prev => [...prev, {
        time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        agent,
        message,
        color
      }]);
    }, delay);
  };

  const handleScenarioChange = (type: string) => {
    setScenario(type);
    setLogs([]);
    setActiveAgent('FRDA');
    
    // Reset then animate
    if (type === 'normal') {
      setRiskScore(12);
      addLog('FRDA', 'Processing video stream...', 'text-cyan-400', 100);
      addLog('FRDA', 'Liveness Challenge: PASSED', 'text-green-400', 800);
      addLog('FRDA', 'No artifacts detected.', 'text-green-400', 1200);
      addLog('TAA', 'User behavior normal. No threat.', 'text-purple-400', 1800);
      addLog('CLA', 'Access Granted.', 'text-green-500', 2400);
      setTimeout(() => setActiveAgent(null), 3000);
    } 
    else if (type === 'spoof') {
      setRiskScore(12);
      // Animate score rising
      setTimeout(() => setRiskScore(45), 500);
      setTimeout(() => setRiskScore(88), 1500);
      setTimeout(() => setRiskScore(99), 2000);

      addLog('FRDA', 'Analyzing facial texture...', 'text-cyan-400', 100);
      addLog('FRDA', 'ALERT: Moiré pattern detected (Screen Replay).', 'text-red-500', 800);
      addLog('FRDA', 'Liveness Challenge: FAILED (No micro-motion).', 'text-red-500', 1500);
      addLog('ADA', 'Dispatched High Priority Fraud Alert.', 'text-blue-400', 2000);
      addLog('TAA', 'Correlating: SIM_SWAP_ATTEMPT context.', 'text-purple-400', 2800);
      addLog('CLA', 'EXECUTING BLOCK: Account Locked.', 'text-red-500', 3500);
      setTimeout(() => setActiveAgent(null), 4000);
    }
    else if (type === 'device') {
      setRiskScore(12);
      // Animate score rising
      setTimeout(() => setRiskScore(30), 500);
      setTimeout(() => setRiskScore(65), 1200);
      setTimeout(() => setRiskScore(85), 2000);

      addLog('FRDA', 'Scanning environment (YOLO11-obj)...', 'text-cyan-400', 100);
      addLog('FRDA', 'Object Detected: Smartphone [Recording posture].', 'text-yellow-400', 1000);
      addLog('ADA', 'Alert: Potential Social Engineering / Spy.', 'text-blue-400', 1800);
      addLog('CLA', 'Action: Masking Sensitive Screen Data.', 'text-red-400', 2600);
      addLog('CLA', 'Prompting Agent: "Do not share OTP".', 'text-red-400', 3200);
      setTimeout(() => setActiveAgent(null), 4000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans p-6 flex flex-col items-center">
      
      {/* Header */}
      <div className="w-full max-w-6xl flex justify-between items-end mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
            FRDA Live Defense
          </h1>
          <p className="text-slate-500 text-sm mt-1">Real-time Fraud & Relationship Defense Agent • SOC Integration v2.4</p>
        </div>
        <div className="flex gap-3">
            <div className="flex items-center gap-2 px-3 py-1 bg-slate-900 rounded border border-slate-700">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs font-mono text-slate-400">SYSTEM ONLINE</span>
            </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Visual Feed */}
        <div className="lg:col-span-2 space-y-6">
          {/* Control Bar */}
          <div className="grid grid-cols-3 gap-4">
             <button 
                onClick={() => handleScenarioChange('normal')}
                className={`p-3 rounded-lg border flex flex-col items-center justify-center gap-2 transition-all ${scenario === 'normal' ? 'bg-green-900/30 border-green-500 text-white' : 'bg-slate-900 border-slate-700 text-slate-500 hover:bg-slate-800'}`}
             >
                <CheckCircle size={20} />
                <span className="text-xs font-bold">SCENARIO 1: NORMAL</span>
             </button>
             <button 
                onClick={() => handleScenarioChange('spoof')}
                className={`p-3 rounded-lg border flex flex-col items-center justify-center gap-2 transition-all ${scenario === 'spoof' ? 'bg-red-900/30 border-red-500 text-white' : 'bg-slate-900 border-slate-700 text-slate-500 hover:bg-slate-800'}`}
             >
                <Scan size={20} />
                <span className="text-xs font-bold">SCENARIO 2: SPOOF</span>
             </button>
             <button 
                onClick={() => handleScenarioChange('device')}
                className={`p-3 rounded-lg border flex flex-col items-center justify-center gap-2 transition-all ${scenario === 'device' ? 'bg-yellow-900/30 border-yellow-500 text-white' : 'bg-slate-900 border-slate-700 text-slate-500 hover:bg-slate-800'}`}
             >
                <Camera size={20} />
                <span className="text-xs font-bold">SCENARIO 3: SPY</span>
             </button>
          </div>

          {/* The Simulated Camera */}
          <CameraFeed scenario={scenario} scanLine={scanLine} isScanning={true} />

          {/* The Agent Workflow Visualization */}
          <SOCPipeline activeAgent={activeAgent} logs={logs} />
        </div>

        {/* Right Column: Analysis */}
        <div className="lg:col-span-1">
           <ThreatVectorPanel riskScore={riskScore} vectorType={scenario} />
           
           {/* Tech Stack Badges */}
           <div className="mt-6 grid grid-cols-2 gap-2">
             <div className="bg-slate-900 p-2 rounded border border-slate-800 text-center">
               <div className="text-[10px] text-slate-500">MODEL</div>
               <div className="text-xs font-bold text-cyan-400">YOLO11-cls</div>
             </div>
             <div className="bg-slate-900 p-2 rounded border border-slate-800 text-center">
               <div className="text-[10px] text-slate-500">LATENCY</div>
               <div className="text-xs font-bold text-green-400">45ms</div>
             </div>
             <div className="bg-slate-900 p-2 rounded border border-slate-800 text-center">
               <div className="text-[10px] text-slate-500">FPS</div>
               <div className="text-xs font-bold text-blue-400">60</div>
             </div>
             <div className="bg-slate-900 p-2 rounded border border-slate-800 text-center">
               <div className="text-[10px] text-slate-500">BACKEND</div>
               <div className="text-xs font-bold text-purple-400">TorchServe</div>
             </div>
           </div>
        </div>

      </div>
    </div>
  );
}
