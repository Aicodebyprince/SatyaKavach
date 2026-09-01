import { Component, type ReactNode } from 'react';
import Icon from './Icon';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('SatyaKavach Error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  handleGoHome = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-ink-950 px-4">
          <div className="glass-card max-w-md p-8 text-center">
            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-red-400/25 bg-red-500/[0.08]">
              <Icon name="alertCircle" className="h-8 w-8 text-red-400" strokeWidth={1.5} />
            </span>

            <h2 className="font-display mt-6 text-xl font-bold text-white">
              कुछ गड़बड़ हो गई / Something went wrong
            </h2>

            <p className="mt-3 text-sm leading-relaxed text-slate-400">
              सत्यकवच को एक त्रुटि का सामना करना पड़ा। कृपया पुनः प्रयास करें।
              <br />
              <span className="text-slate-500">
                SatyaKavach encountered an error. Please try again.
              </span>
            </p>

            {this.state.error && (
              <details className="mt-4 rounded-lg border border-white/[0.06] bg-black/30 p-3 text-left">
                <summary className="cursor-pointer font-mono text-xs text-slate-500">
                  Technical details
                </summary>
                <pre className="mt-2 overflow-auto text-xs text-red-300/80">
                  {this.state.error.message}
                </pre>
              </details>
            )}

            <div className="mt-6 flex justify-center gap-3">
              <button onClick={this.handleReset} className="btn-outline">
                पुनः प्रयास करें / Retry
              </button>
              <button onClick={this.handleGoHome} className="btn-primary">
                होम / Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
