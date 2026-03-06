import { Link } from 'react-router';
import { Calendar, Lightbulb, User } from 'lucide-react';

export function Home() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-white/50 px-8 py-4 flex items-center justify-end">
        <div className="flex items-center gap-3">
          <User className="w-8 h-8 text-gray-400 bg-gray-200 rounded-full p-1.5" />
          <span className="text-sm text-gray-600">hongi234@email.com</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-8 py-12">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">환영합니다!</h1>
          <p className="text-gray-600 text-lg">지금 건강 상태에 맞는 영양제를 추천받아 보세요.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-5xl">
          {/* 분석 기록 Card */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-14 h-14 bg-yellow-100 rounded-2xl flex items-center justify-center">
                <Lightbulb className="w-8 h-8 text-yellow-500" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">분석 기록</h2>
            </div>

            <div className="mb-6 space-y-2">
              <div className="h-3 bg-gray-100 rounded w-full"></div>
              <div className="h-3 bg-gray-100 rounded w-5/6"></div>
              <div className="h-3 bg-gray-100 rounded w-4/6"></div>
            </div>

            <p className="text-gray-700 mb-4 leading-relaxed">
              선택한 영양제의 성분을 분석하고,
              <br />
              건강 상태를 경기맨딩 기록합니다.
              <br />
              복용 시간, 용량, 주기를 기록하여
              <br />
              나의 건강 관리 이력을 체계적으로
            </p>

            <div className="mb-6">
              <span className="text-gray-900 font-medium">분석 기록 </span>
              <Link 
                to="/analysis-history" 
                className="text-orange-500 font-bold hover:underline cursor-pointer">3건
              </Link>
            </div>
            <Link
              to="/recommendation"
              className="block w-full bg-blue-500 text-white text-center py-3 rounded-xl font-medium hover:bg-blue-600 transition-colors">추천받기 ›
            </Link>
          </div>

          {/* 기록하기 Card */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center">
                <Calendar className="w-8 h-8 text-blue-500" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">기록하기</h2>
            </div>

            <div className="mb-6 space-y-2">
              <div className="h-3 bg-gray-100 rounded w-full"></div>
              <div className="h-3 bg-gray-100 rounded w-5/6"></div>
              <div className="h-3 bg-gray-100 rounded w-4/6"></div>
            </div>

            <p className="text-gray-700 mb-8 leading-relaxed">
              선택 중인 영양제에 대한 복용 정보를
              <br />
              관리할 수 있습니다.
              <br />
              복용 시간, 용량, 주기를 기록하여
              <br />
              나의 건강 관리 이력을 체계적으로 관리해 보세요.
            </p>

            <Link
              to="/record"
              className="block w-full bg-blue-500 text-white text-center py-3 rounded-xl font-medium hover:bg-blue-600 transition-colors"
            >
              기록하기 ›
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}