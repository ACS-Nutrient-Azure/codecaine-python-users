import { MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router';
import { useState, useEffect } from 'react';

// 백엔드에서 받을 데이터의 타입을 미리 정의해 둡니다. (TypeScript 사용 시)
interface RecordType {
  id: number; // DB에서 내려주는 고유 ID가 있으면 리스트 렌더링에 좋습니다.
  date: string;
  title: string;
}

export function AnalysisHistory() {
  const navigate = useNavigate();

  // 1. 데이터를 저장할 상태 (초기값은 빈 배열)
  const [records, setRecords] = useState<RecordType[]>([]);
  // 2. 로딩 상태를 관리할 상태
  const [isLoading, setIsLoading] = useState(true);
  // 3. 에러 발생 시 처리할 상태
  const [error, setError] = useState<string | null>(null);

  // 컴포넌트가 처음 화면에 나타날 때(mount) 백엔드에 데이터를 요청합니다.
  useEffect(() => {
    const fetchRecords = async () => {
      try {
        setIsLoading(true);
        
        // =========================================================
        // 🚨 나중에 Python 백엔드가 완성되면 아래 주석을 풀고 적용하세요.
        // const response = await fetch('http://localhost:8000/api/analysis/history');
        // if (!response.ok) throw new Error('네트워크 응답이 좋지 않습니다.');
        // const data = await response.json();
        // setRecords(data);
        // =========================================================

        // 지금은 백엔드가 없으므로, 통신하는 '척' 1초 딜레이를 줍니다. (Mock API)
        setTimeout(() => {
          const mockData = [
            { id: 1, date: '2026.02.10', title: '영양제 추천 결과' },
            { id: 2, date: '2026.02.05', title: '영양제 추천 결과' },
            { id: 3, date: '2026.02.01', title: '영양제 추천 결과' },
          ];
          setRecords(mockData);
          setIsLoading(false); // 데이터 로딩 완료
        }, 1000);

      } catch (err) {
        setError('데이터를 불러오는 데 실패했습니다.');
        setIsLoading(false);
      }
    };

    fetchRecords();
  }, []);

  const handleViewDetail = (recordId: number) => {
    // 추천 결과 카드를 클릭하면 해당 결과 페이지로 이동
    // 실제로는 recordId를 쿼리 파라미터나 state로 전달할 수 있습니다.
    // navigate(`/recommendation-result?id=${recordId}`);
    navigate('/recommendation-result');
  };

  const handleChatbotClick = (e: React.MouseEvent, recordId: number) => {
    // 이벤트 버블링을 막아서 카드 클릭 이벤트가 발생하지 않도록 합니다.
    e.stopPropagation();
    // 상담하기 버튼을 클릭하면 챗봇 페이지로 이동
    // navigate(`/chatbot?recordId=${recordId}`);
    navigate('/chatbot');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-sm p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">분석 기록</h1>

          <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
              <MessageSquare className="w-5 h-5 text-gray-500" />
            </div>
            <p className="text-gray-700 pt-2">홍길동님의 영양제 추천 분석 기록입니다.</p>
          </div>

          <div className="space-y-4">
            {/* 로딩 중일 때 보여줄 UI */}
            {isLoading && (
              <div className="text-center py-8 text-gray-500">
                기록을 불러오는 중입니다...
              </div>
            )}

            {/* 에러가 발생했을 때 보여줄 UI */}
            {error && (
              <div className="text-center py-8 text-red-500">
                {error}
              </div>
            )}

            {/* 로딩도 끝났고 에러도 없는데 데이터가 없을 때 */}
            {!isLoading && !error && records.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                아직 분석 기록이 없습니다.
              </div>
            )}

            {/* 정상적으로 데이터를 불러왔을 때 */}
            {!isLoading && !error && records.map((record) => (
              <div
                key={record.id} // 배열의 index 대신 고유 id를 사용하는 것이 성능상 좋습니다.
                className="flex items-center justify-between p-6 border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer"
                onClick={() => handleViewDetail(record.id)}
              >
                <div>
                  <p className="text-sm text-gray-500 mb-1">{record.date}</p>
                  <h3 className="text-lg font-medium text-gray-900">{record.title}</h3>
                </div>
                <button 
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                  onClick={(e) => handleChatbotClick(e, record.id)}
                >
                  <MessageSquare className="w-4 h-4" />
                  <span className="text-sm">상담하기</span>
                  <span className="text-gray-400">›</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}