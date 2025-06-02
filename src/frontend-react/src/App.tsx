import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import debug helpers (makes them available as window.debug)
import './utils/debugHelpers';

// Components
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import AnalysisPage from './pages/AnalysisPage';
import ResultsPage from './pages/ResultsPage';
import CompetitorFinderPage from './pages/CompetitorFinderPage';
import FocusAreaPage from './pages/FocusAreaPage';
import StreamingTestPage from './pages/StreamingTestPage';
import StreamingTest from './components/StreamingTest';
import CachedStreamingTest from './components/CachedStreamingTest';
import ErrorBoundary from './components/ErrorBoundary';

import './App.css';

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Header />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/analysis" element={<AnalysisPage />} />
                <Route path="/results/:analysisId" element={<ResultsPage />} />
                <Route path="/competitors" element={<CompetitorFinderPage />} />
                <Route path="/focus-areas" element={<FocusAreaPage />} />
                <Route path="/streaming-test" element={<StreamingTestPage />} />
                <Route path="/streaming-improved" element={<StreamingTest />} />
                <Route path="/cached-streaming" element={<CachedStreamingTest />} />
              </Routes>
            </main>
          </div>
        </Router>
      </ErrorBoundary>
    </QueryClientProvider>
  );
}

export default App;
