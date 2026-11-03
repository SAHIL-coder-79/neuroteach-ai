import React from 'react';
import { AlertCircle, RotateCcw, Clock, ArrowRight } from 'lucide-react';

interface StateCardProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  actionText?: string;
}

export const LoadingState: React.FC<{ label?: string }> = ({ label = "Loading pedagogical data..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center space-y-4">
      <div className="h-10 w-10 border-2 border-accent-500/20 border-t-accent-500 rounded-full animate-spin" />
      <p className="text-sm text-text-muted font-medium">{label}</p>
    </div>
  );
};

export const ErrorState: React.FC<StateCardProps> = ({
  title = "Something went wrong",
  message = "Failed to communicate with service. The system will fall back to static verified resources.",
  onRetry,
  actionText = "Try Again"
}) => {
  return (
    <div className="p-6 rounded-card bg-danger/10 border border-danger/30 text-center flex flex-col items-center max-w-lg mx-auto space-y-3">
      <div className="h-10 w-10 rounded-full bg-danger/20 flex items-center justify-center text-danger">
        <AlertCircle className="h-5 w-5" />
      </div>
      <div>
        <h4 className="text-base font-semibold text-danger">{title}</h4>
        <p className="text-xs text-text-muted mt-1 leading-relaxed">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 text-xs font-semibold rounded-lg bg-danger/20 text-danger hover:bg-danger/30 border border-danger/40 flex items-center gap-2 transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>{actionText}</span>
        </button>
      )}
    </div>
  );
};

export const EmptyState: React.FC<{
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}> = ({
  title,
  description,
  actionLabel,
  onAction
}) => {
  return (
    <div className="p-10 rounded-card bg-bg-surface border border-border-subtle text-center flex flex-col items-center justify-center space-y-3">
      <div className="h-12 w-12 rounded-xl bg-bg-raised border border-border-subtle flex items-center justify-center text-text-muted">
        <Clock className="h-6 w-6" />
      </div>
      <div className="max-w-md">
        <h4 className="text-sm font-semibold text-text-primary">{title}</h4>
        <p className="text-xs text-text-muted mt-1 leading-relaxed">{description}</p>
      </div>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-2 px-4 py-2 text-xs font-semibold rounded-lg bg-accent-500 text-white hover:bg-accent-600 transition-colors flex items-center gap-1.5"
        >
          <span>{actionLabel}</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
};
