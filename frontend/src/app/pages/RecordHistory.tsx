import { useState } from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';

type Supplement = {
  id: number;
  name: string;
  color: string;
  dailyLimit: number; // 하루 복용 횟수
  records: Record<string, number>; // 날짜별 복용 횟수 (예: "2024-04-05": 2)
};

export function RecordHistory() {
  const [currentDate, setCurrentDate] = useState(new Date(2024, 3)); // April 2024
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  // 스캔된 데이터로부터 자동 생성된 영양제 정보
  const [supplements, setSupplements] = useState<Supplement[]>([
    {
      id: 1,
      name: 'Omega-3',
      color: 'bg-orange-400',
      dailyLimit: 2,
      records: {
        '2024-04-01': 2,
        '2024-04-05': 1,
        '2024-04-10': 2,
        '2024-04-15': 2,
        '2024-04-19': 1,
        '2024-04-22': 2,
        '2024-04-26': 1,
      },
    },
    {
      id: 2,
      name: '비타민 D',
      color: 'bg-yellow-400',
      dailyLimit: 1,
      records: {
        '2024-04-03': 1,
        '2024-04-08': 1,
        '2024-04-17': 1,
        '2024-04-24': 1,
        '2024-04-29': 1,
      },
    },
    {
      id: 3,
      name: '멀티비타민',
      color: 'bg-green-500',
      dailyLimit: 3,
      records: {
        '2024-04-04': 2,
        '2024-04-08': 3,
        '2024-04-15': 1,
        '2024-04-28': 2,
      },
    },
    {
      id: 4,
      name: 'Vitamin C',
      color: 'bg-red-400',
      dailyLimit: 2,
      records: {
        '2024-04-02': 1,
        '2024-04-10': 2,
        '2024-04-18': 2,
      },
    },
    {
      id: 5,
      name: '유산균',
      color: 'bg-purple-400',
      dailyLimit: 1,
      records: {
        '2024-04-05': 1,
        '2024-04-12': 1,
        '2024-04-20': 1,
      },
    },
    {
      id: 6,
      name: '비타민 B Complex',
      color: 'bg-blue-400',
      dailyLimit: 2,
      records: {
        '2024-04-07': 1,
        '2024-04-14': 2,
        '2024-04-21': 1,
      },
    },
  ]);

  const daysInMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth() + 1,
    0
  ).getDate();
  const firstDayOfMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth(),
    1
  ).getDay();

  const monthNames = [
    '1월',
    '2월',
    '3월',
    '4월',
    '5월',
    '6월',
    '7월',
    '8월',
    '9월',
    '10월',
    '11월',
    '12월',
  ];

  const formatDateKey = (year: number, month: number, day: number) => {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  };

  const getSupplementsForDay = (day: number) => {
    const dateKey = formatDateKey(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      day
    );
    return supplements
      .map((s) => ({
        ...s,
        count: s.records[dateKey] || 0,
      }))
      .filter((s) => s.count > 0);
  };

  const goToPreviousMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() - 1)
    );
    setSelectedDate(null);
  };

  const goToNextMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() + 1)
    );
    setSelectedDate(null);
  };

  const handleDateClick = (day: number) => {
    const dateKey = formatDateKey(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      day
    );
    setSelectedDate(dateKey);
  };

  const handleSupplementClick = (supplementId: number, dateKey: string) => {
    setSupplements((prevSupplements) =>
      prevSupplements.map((supplement) => {
        if (supplement.id === supplementId) {
          const currentCount = supplement.records[dateKey] || 0;
          const newRecords = { ...supplement.records };

          // 다음 횟수로 증가, dailyLimit 도달 시 다시 0으로
          if (currentCount < supplement.dailyLimit) {
            newRecords[dateKey] = currentCount + 1;
          } else {
            delete newRecords[dateKey];
          }

          return {
            ...supplement,
            records: newRecords,
          };
        }
        return supplement;
      })
    );
  };

  const getCountForDate = (
    supplementId: number,
    dateKey: string | null
  ): number => {
    if (!dateKey) return 0;
    const supplement = supplements.find((s) => s.id === supplementId);
    return supplement?.records[dateKey] || 0;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto flex gap-6">
        {/* Main Calendar Section */}
        <div className={`bg-white rounded-2xl shadow-sm p-8 transition-all duration-300 ${selectedDate ? 'flex-1' : 'w-full max-w-5xl mx-auto'}`}>
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              영양제 섭취 기록
            </h1>
            <p className="text-gray-600">
              스캔된 영양제 정보를 기반으로 매일 복용 기록을 관리하세요.
            </p>
          </div>

          <div className="flex items-center justify-between mb-6">
            <button
              onClick={goToPreviousMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900">
                {currentDate.getFullYear()}년{' '}
                {monthNames[currentDate.getMonth()]}
              </h2>
            </div>

            <button
              onClick={goToNextMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Calendar */}
          <div className="grid grid-cols-7 gap-2">
            {['월', '화', '수', '목', '금', '토', '일'].map((day, index) => (
              <div
                key={day}
                className={`text-center py-3 font-medium ${
                  index === 6 ? 'text-red-500' : 'text-gray-600'
                }`}
              >
                {day}
              </div>
            ))}

            {/* Empty cells for days before month starts */}
            {Array.from({
              length: firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1,
            }).map((_, index) => (
              <div key={`empty-${index}`} className="aspect-square" />
            ))}

            {/* Calendar days */}
            {Array.from({ length: daysInMonth }).map((_, index) => {
              const day = index + 1;
              const daySupplements = getSupplementsForDay(day);
              const isToday = day === 24;
              const dateKey = formatDateKey(
                currentDate.getFullYear(),
                currentDate.getMonth(),
                day
              );
              const isSelected = selectedDate === dateKey;
              
              // 최대 3개만 캘린더에 표시
              const displaySupplements = daySupplements.slice(0, 3);
              const hasMore = daySupplements.length > 3;

              return (
                <div
                  key={day}
                  onClick={() => handleDateClick(day)}
                  className={`aspect-square border rounded-lg p-2 hover:bg-gray-50 cursor-pointer transition-colors ${
                    isToday
                      ? 'border-blue-500 border-2 bg-blue-50'
                      : isSelected
                      ? 'border-blue-400 border-2 bg-blue-50'
                      : 'border-gray-200'
                  }`}
                >
                  <div
                    className={`text-sm mb-1 ${
                      isToday
                        ? 'font-bold text-blue-600'
                        : isSelected
                        ? 'font-bold text-blue-500'
                        : 'text-gray-700'
                    }`}
                  >
                    {day}
                  </div>
                  <div className="space-y-1">
                    {displaySupplements.map((supplement, idx) => (
                      <div
                        key={idx}
                        className={`${supplement.color} text-white text-xs px-1.5 py-0.5 rounded flex items-center justify-between gap-1`}
                      >
                        <span className="truncate text-[10px]">
                          {supplement.name}
                        </span>
                        <span className="text-[9px] font-bold opacity-90">
                          {supplement.count}/{supplement.dailyLimit}
                        </span>
                      </div>
                    ))}
                    {hasMore && (
                      <div className="text-[9px] text-gray-500 text-center font-medium">
                        +{daySupplements.length - 3}개 더
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-3">
              복용 중인 영양제 (스캔 데이터 기반)
            </p>
            <div className="flex gap-4 flex-wrap">
              {supplements.map((supplement) => (
                <div
                  key={supplement.name}
                  className="flex items-center gap-2"
                >
                  <div
                    className={`w-3 h-3 ${supplement.color} rounded-full`}
                  ></div>
                  <span className="text-sm text-gray-700">
                    {supplement.name} (1일 {supplement.dailyLimit}회)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Slide Panel for Selected Date */}
        {selectedDate && (
          <div className="w-96 bg-white rounded-2xl shadow-lg p-6 animate-slide-in-right">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-gray-900">
                {currentDate.getFullYear()}년{' '}
                {monthNames[currentDate.getMonth()]}{' '}
                {parseInt(selectedDate.split('-')[2])}일
              </h3>
              <button
                onClick={() => setSelectedDate(null)}
                className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-3">
                영양제 이름을 클릭하여 복용 횟수를 기록하세요
              </p>
            </div>

            <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
              {supplements.map((supplement) => {
                const count = getCountForDate(supplement.id, selectedDate);
                const isComplete = count >= supplement.dailyLimit;

                return (
                  <button
                    key={supplement.id}
                    onClick={() =>
                      !isComplete &&
                      handleSupplementClick(supplement.id, selectedDate)
                    }
                    disabled={isComplete}
                    className={`w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all ${
                      isComplete
                        ? 'border-gray-300 bg-gray-200 cursor-not-allowed opacity-60'
                        : count > 0
                        ? 'border-blue-400 bg-blue-50 hover:bg-blue-100'
                        : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-4 h-4 ${supplement.color} rounded-full`}
                      ></div>
                      <span
                        className={`text-sm font-medium ${
                          isComplete ? 'text-gray-500 line-through' : 'text-gray-700'
                        }`}
                      >
                        {supplement.name}
                      </span>
                    </div>
                    <div
                      className={`text-base font-bold ${
                        isComplete
                          ? 'text-gray-500'
                          : count > 0
                          ? 'text-blue-600'
                          : 'text-gray-400'
                      }`}
                    >
                      {count}/{supplement.dailyLimit}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                * 모든 횟수를 채운 영양제는 회색으로 표시되며 클릭할 수 없습니다.
              </p>
            </div>
          </div>
        )}
      </div>
      
      <style>{`
        @keyframes slide-in-right {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        .animate-slide-in-right {
          animation: slide-in-right 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}