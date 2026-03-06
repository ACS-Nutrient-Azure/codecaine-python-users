import { Link, Outlet, useLocation } from 'react-router';
import { Calendar, Lightbulb, User, FileText, Settings } from 'lucide-react';

export function Layout() {
  const location = useLocation();

  const menuItems = [
    { path: '/recommendation', icon: Lightbulb, label: '분석하기' },
    { path: '/record', icon: Calendar, label: '기록하기' },
    { path: '/my-page', icon: User, label: '내 정보관리' },
    { path: '/analysis-history', icon: FileText, label: '분석 리포트' },
    { path: '/settings', icon: Settings, label: '설정' },
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-blue-100">
      {/* Sidebar */}
      <aside className="w-56 bg-white/80 backdrop-blur-sm flex flex-col">
        <div className="p-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <div className="w-5 h-5 border-2 border-white rounded-full"></div>
            </div>
            <span className="font-bold text-xl text-gray-900">Portal</span>
          </Link>
        </div>

        <nav className="flex-1 px-4 pt-8">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all ${
                  isActive
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}