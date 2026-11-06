import {
  BookOpen,
  ArrowLeft,
  GitBranch,
  Calculator,
  Table,
  Play,
  Network,
  GraduationCap,
  TreePine,
  type LucideIcon,
} from 'lucide-react';
import type { ActiveSection } from '../types';

interface NavItem {
  id: ActiveSection;
  label: string;
  icon: LucideIcon;
  color: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'grammar', label: 'Grammar Workspace', icon: BookOpen, color: 'text-blue-400' },
  { id: 'left-recursion', label: 'Left Recursion', icon: ArrowLeft, color: 'text-cyan-400' },
  { id: 'left-factoring', label: 'Left Factoring', icon: GitBranch, color: 'text-violet-400' },
  { id: 'first-follow', label: 'FIRST & FOLLOW', icon: Calculator, color: 'text-emerald-400' },
  { id: 'parsing-table', label: 'LL(1) Table', icon: Table, color: 'text-amber-400' },
  { id: 'parsing-simulator', label: 'Parsing Simulator', icon: Play, color: 'text-orange-400' },
  { id: 'parse-tree', label: 'Parse Tree', icon: Network, color: 'text-pink-400' },
  { id: 'practice', label: 'Practice Mode', icon: GraduationCap, color: 'text-indigo-400' },
];

interface SidebarProps {
  activeSection: ActiveSection;
  onSectionChange: (section: ActiveSection) => void;
  isCollapsed?: boolean;
}

export function Sidebar({ activeSection, onSectionChange, isCollapsed = false }: SidebarProps) {
  return (
    <aside
      className="h-full flex flex-col bg-[#0f172a] border-r border-gray-800/60"
      style={{ width: isCollapsed ? 64 : 240 }}
    >
      {/* Logo area */}
      <div className="flex items-center gap-2.5 px-4 py-4 border-b border-gray-800/60">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center flex-shrink-0 shadow-glow-blue">
          <TreePine size={16} className="text-white" />
        </div>
        {!isCollapsed && (
          <div>
            <p className="text-sm font-bold text-white">ParseViz</p>
            <p className="text-xs text-gray-500">LL(1) Parser</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto scrollbar-thin">
        {!isCollapsed && (
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider px-2 py-1.5 mb-1">
            Sections
          </p>
        )}

        {NAV_ITEMS.map((item) => {
          const isActive = activeSection === item.id;
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              title={isCollapsed ? item.label : undefined}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                transition-all duration-200 group relative
                ${isActive
                  ? 'bg-gradient-to-r from-blue-600/30 to-cyan-600/20 text-white border border-blue-500/30 shadow-glow-blue'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
                }
              `}
            >
              {/* Active indicator */}
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-gradient-to-b from-blue-400 to-cyan-400 rounded-r-full" />
              )}

              <Icon
                size={17}
                className={`flex-shrink-0 transition-colors ${
                  isActive ? item.color : 'text-gray-500 group-hover:' + item.color
                }`}
              />

              {!isCollapsed && (
                <span className={`truncate ${isActive ? 'text-white' : ''}`}>
                  {item.label}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="px-4 py-3 border-t border-gray-800/60">
          <p className="text-xs text-gray-600">
            Compiler Design · LL(1) Parsing
          </p>
          <div className="flex gap-1 mt-1">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse-slow" />
            <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse-slow" style={{ animationDelay: '0.3s' }} />
            <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse-slow" style={{ animationDelay: '0.6s' }} />
          </div>
        </div>
      )}
    </aside>
  );
}
