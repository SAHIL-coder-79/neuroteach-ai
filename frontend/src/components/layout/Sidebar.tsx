import React from 'react';
import { 
  Home, 
  Sparkles, 
  Map, 
  CheckSquare, 
  Clock, 
  Users, 
  Network, 
  BarChart3, 
  ChevronLeft,
  ChevronRight,
  BrainCircuit,
  LucideIcon
} from 'lucide-react';

export type NavItemKey = 
  | 'home'
  | 'ask_neuro'
  | 'roadmap'
  | 'practice'
  | 'sessions'
  | 'roleplay'
  | 'workshop'
  | 'scenarios'
  | 'library'
  | 'mind_map'
  | 'evaluator'
  | 'feedback';

interface NavItemConfig {
  key: NavItemKey;
  label: string;
  icon: LucideIcon;
  badge?: string;
  isMvp: boolean;
}

const NAV_ITEMS: NavItemConfig[] = [
  { key: 'home', label: 'Home', icon: Home, isMvp: true },
  { key: 'ask_neuro', label: 'Ask Neuro', icon: Sparkles, badge: 'MVP', isMvp: true },
  { key: 'roadmap', label: 'Roadmap', icon: Map, badge: 'MVP', isMvp: true },
  { key: 'practice', label: 'Practice', icon: CheckSquare, badge: 'MVP', isMvp: true },
  { key: 'sessions', label: 'Sessions', icon: Clock, badge: 'Active', isMvp: true },
  { key: 'roleplay', label: 'Roleplay', icon: Users, badge: 'Preview', isMvp: true },
  { key: 'mind_map', label: 'Mind Map', icon: Network, badge: 'Preview', isMvp: true },
  { key: 'evaluator', label: 'Evaluator', icon: BarChart3, badge: 'MVP', isMvp: true },
];

interface SidebarProps {
  currentNav: NavItemKey;
  onSelectNav: (key: NavItemKey) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentNav,
  onSelectNav,
  collapsed,
  onToggleCollapse
}) => {
  return (
    <aside 
      className={`relative h-screen bg-bg-surface border-r border-border-subtle flex flex-col justify-between transition-all duration-200 z-30 select-none ${
        collapsed ? 'w-[72px]' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 border-b border-border-subtle flex items-center justify-between px-4">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="h-9 w-9 shrink-0 rounded-xl bg-accent-500 flex items-center justify-center text-white shadow-sm">
              <BrainCircuit className="h-5 w-5" />
            </div>
            {!collapsed && (
              <div className="leading-tight">
                <span className="font-bold text-sm tracking-tight text-text-primary block">NEUROTEACH</span>
                <span className="text-[10px] text-accent-500 uppercase tracking-wider font-semibold">Pedagogy AI</span>
              </div>
            )}
          </div>

          <button
            onClick={onToggleCollapse}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="h-7 w-7 rounded-lg text-text-muted hover:text-text-primary hover:bg-bg-raised flex items-center justify-center transition-colors"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Navigation list */}
        <div className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = currentNav === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onSelectNav(item.key)}
                title={collapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-accent-lavender dark:bg-[#241E3E] text-accent-700 dark:text-accent-300 shadow-xs'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-raised'
                }`}
              >
                <Icon className={`h-4 w-4 shrink-0 transition-colors ${isActive ? 'text-accent-500' : 'text-text-muted'}`} />
                
                {!collapsed && (
                  <div className="flex-1 flex items-center justify-between overflow-hidden">
                    <span className="truncate text-left">{item.label}</span>
                    {item.badge && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                        item.isMvp 
                          ? 'bg-bg-surface text-accent-500 border border-accent-200 dark:border-accent-500/30'
                          : 'bg-bg-raised text-text-muted'
                      }`}>
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* User / Status Footer */}
      <div className="p-3 border-t border-border-subtle bg-bg-surface">
        {!collapsed ? (
          <div className="flex items-center gap-3 p-2 rounded-xl bg-bg-raised border border-border-subtle">
            <div className="h-8 w-8 rounded-full bg-accent-lavender dark:bg-[#241E3E] border border-accent-200 dark:border-accent-500/30 flex items-center justify-center text-accent-700 dark:text-accent-300 text-xs font-bold">
              NT
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-text-primary truncate">Aarav (Student)</p>
              <p className="text-[10px] text-text-muted truncate">CS / IT Semester Sprint</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-8 w-8 rounded-full bg-accent-lavender dark:bg-[#241E3E] border border-accent-200 dark:border-accent-500/30 flex items-center justify-center text-accent-700 dark:text-accent-300 text-xs font-bold">
              NT
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
