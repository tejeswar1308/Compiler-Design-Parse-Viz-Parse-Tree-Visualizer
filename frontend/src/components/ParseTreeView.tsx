import { useMemo, useCallback, useState, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  MiniMap,
  NodeProps,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, Download, Info, CheckCircle2 } from 'lucide-react';
import { computeTreeLayout } from '../utils/treeLayout';
import type { ParseResult, TreeNode } from '../types';

// --- Custom node components ---

function NonterminalNode({ data, selected }: NodeProps) {
  return (
    <div
      className={`px-3 py-2 rounded-lg bg-blue-950/90 border-2 ${
        selected ? 'border-cyan-400 ring-2 ring-cyan-400/50' : 'border-blue-500'
      } text-blue-100 font-mono text-sm font-semibold shadow-lg min-w-[70px] text-center transition-all cursor-pointer`}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#3b82f6' }} />
      <div>{data.label as string}</div>
      {data.production && (
        <div className="text-[10px] text-blue-300 font-normal opacity-80 truncate max-w-[120px]">
          {data.production as string}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: '#3b82f6' }} />
    </div>
  );
}

function TerminalNode({ data, selected }: NodeProps) {
  return (
    <div
      className={`px-3 py-2 rounded-lg bg-emerald-950/90 border-2 ${
        selected ? 'border-emerald-300 ring-2 ring-emerald-400/50' : 'border-emerald-500'
      } text-emerald-100 font-mono text-sm font-semibold shadow-lg min-w-[60px] text-center transition-all cursor-pointer`}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#10b981' }} />
      {data.label as string}
      <Handle type="source" position={Position.Bottom} style={{ background: '#10b981' }} />
    </div>
  );
}

function EpsilonNode({ data, selected }: NodeProps) {
  return (
    <div
      className={`px-3 py-2 rounded-lg bg-slate-900 border-2 ${
        selected ? 'border-purple-400 ring-2 ring-purple-400/50' : 'border-slate-600'
      } text-slate-300 font-mono text-sm shadow min-w-[50px] text-center transition-all cursor-pointer`}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#64748b' }} />
      {data.label as string}
      <Handle type="source" position={Position.Bottom} style={{ background: '#64748b' }} />
    </div>
  );
}

const nodeTypes = {
  nonterminal: NonterminalNode,
  terminal: TerminalNode,
  epsilon: EpsilonNode,
};

function buildFlowElements(root: TreeNode): { nodes: Node[]; edges: Edge[] } {
  const layout = computeTreeLayout(root);

  const nodes: Node[] = layout.nodes.map((n) => ({
    id: n.id,
    type: n.type,
    position: { x: n.x, y: n.y },
    data: { label: n.label, type: n.type, production: n.production },
  }));

  const edges: Edge[] = layout.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    style: { stroke: '#475569', strokeWidth: 2 },
    animated: false,
  }));

  return { nodes, edges };
}

interface ParseTreeViewProps {
  parseResult: ParseResult | null;
}

export function ParseTreeView({ parseResult }: ParseTreeViewProps) {
  const [selectedNodeData, setSelectedNodeData] = useState<{
    id: string;
    label: string;
    type: string;
    production?: string;
  } | null>(null);

  const hasTree = !!(parseResult?.accepted && parseResult.parse_tree);

  const initialElements = useMemo(() => {
    if (!hasTree || !parseResult?.parse_tree) return { nodes: [], edges: [] };
    return buildFlowElements(parseResult.parse_tree);
  }, [hasTree, parseResult]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialElements.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialElements.edges);

  useEffect(() => {
    setNodes(initialElements.nodes);
    setEdges(initialElements.edges);
    setSelectedNodeData(null);
  }, [initialElements, setNodes, setEdges]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeData({
      id: node.id,
      label: node.data.label,
      type: node.data.type || node.type || 'unknown',
      production: node.data.production,
    });
  }, []);

  const handleExport = useCallback(() => {
    const svgEl = document.querySelector('.react-flow__renderer svg');
    if (!svgEl) return;
    const svg = svgEl.outerHTML;
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parse-tree.svg';
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4 max-w-6xl mx-auto"
    >
      {/* Title */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <Network size={20} className="text-cyan-400" />
          <h2 className="text-xl font-semibold text-white">Parse Tree Visualizer</h2>
        </div>
        {hasTree && (
          <button onClick={handleExport} className="btn-secondary text-sm">
            <Download size={15} />
            Export SVG
          </button>
        )}
      </div>

      {/* Legend & Stats */}
      {hasTree && (
        <div className="flex items-center justify-between gap-4 flex-wrap bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="flex items-center gap-4 flex-wrap">
            <LegendItem color="bg-blue-950 border-blue-500" label="Nonterminal" />
            <LegendItem color="bg-emerald-950 border-emerald-500" label="Terminal" />
            <LegendItem color="bg-slate-900 border-slate-600" label="Epsilon (ε)" />
          </div>
          <div className="text-xs text-slate-400">
            Click any node to inspect its derivation details.
          </div>
        </div>
      )}

      {/* Canvas */}
      {hasTree ? (
        <div className="card p-0 overflow-hidden relative" style={{ height: 530 }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.25 }}
            minZoom={0.2}
            maxZoom={2.5}
            style={{ background: '#0a0f1e' }}
          >
            <Background color="#1e293b" variant={BackgroundVariant.Dots} gap={20} />
            <Controls style={{ background: '#1e293b', border: '1px solid #334155' }} />
            <MiniMap
              style={{ background: '#0f172a', border: '1px solid #334155' }}
              nodeColor={(n) => {
                if (n.type === 'nonterminal') return '#3b82f6';
                if (n.type === 'terminal') return '#10b981';
                return '#64748b';
              }}
            />
          </ReactFlow>

          {/* Node details overlay card */}
          <AnimatePresence>
            {selectedNodeData && (
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 15 }}
                className="absolute bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:w-80 bg-slate-900/95 border border-cyan-500/40 backdrop-blur rounded-xl p-4 shadow-2xl z-20 text-xs"
              >
                <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
                  <div className="flex items-center gap-1.5 font-semibold text-cyan-300">
                    <Info size={14} /> Node Details
                  </div>
                  <button
                    onClick={() => setSelectedNodeData(null)}
                    className="text-slate-400 hover:text-white"
                  >
                    ✕
                  </button>
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Symbol:</span>
                    <span className="font-mono font-bold text-white text-sm">{selectedNodeData.label}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Category:</span>
                    <span className="capitalize font-medium text-slate-200">{selectedNodeData.type}</span>
                  </div>
                  {selectedNodeData.production && (
                    <div className="pt-1 border-t border-slate-800">
                      <span className="text-slate-400 block mb-1">Expansion Rule Applied:</span>
                      <span className="font-mono bg-blue-950/80 border border-blue-700/50 text-blue-200 px-2 py-0.5 rounded block">
                        {selectedNodeData.production}
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ) : (
        <div className="card" style={{ height: 420 }}>
          <div className="empty-state h-full">
            <Network size={48} className="text-gray-700 mb-4" />
            {!parseResult && (
              <>
                <p className="text-gray-400 font-medium">No parse tree generated yet</p>
                <p className="text-gray-600 text-sm mt-1">
                  Enter or load a grammar, validate it, and run a test string in the Parsing Simulator.
                </p>
              </>
            )}
            {parseResult && !parseResult.accepted && (
              <>
                <p className="text-red-400 font-medium">Input string was rejected</p>
                <p className="text-gray-600 text-sm mt-1">
                  A parse tree is constructed only for strings that are accepted by the LL(1) grammar.
                </p>
              </>
            )}
            {parseResult?.accepted && !parseResult.parse_tree && (
              <>
                <p className="text-amber-400 font-medium">Parse tree could not be derived</p>
                <p className="text-gray-600 text-sm mt-1">
                  No derivation steps were returned.
                </p>
              </>
            )}
          </div>
        </div>
      )}

      {/* Productions used summary */}
      {parseResult?.accepted && parseResult.productions_used.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 size={16} className="text-green-400" />
            <p className="text-sm font-semibold text-slate-200">
              Derivation Sequence ({parseResult.productions_used.length} productions applied)
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {parseResult.productions_used.map((prod, i) => (
              <span
                key={i}
                className="font-mono text-xs bg-slate-900 border border-slate-700 text-cyan-300 px-2.5 py-1 rounded-md shadow-sm"
              >
                <span className="text-slate-500 mr-1.5">{i + 1}.</span>
                {prod}
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-3.5 h-3.5 rounded border-2 ${color}`} />
      <span className="text-xs text-slate-300">{label}</span>
    </div>
  );
}
