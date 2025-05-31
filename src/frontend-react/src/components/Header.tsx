import { Link, useLocation } from 'react-router-dom';
import { Target, Activity, BarChart3 } from 'lucide-react';

const Header = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 gradient-primary rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient-primary">
                Orthopedic Intelligence
              </h1>
              <p className="text-sm text-gray-600">
                Competitive Intelligence Platform
              </p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-8">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span className="font-medium">Dashboard</span>
            </Link>

            <Link
              to="/analysis"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/analysis') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span className="font-medium">New Analysis</span>
            </Link>
          </nav>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-opportunity-500 rounded-full"></div>
            <span className="text-sm text-gray-600">System Online</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 