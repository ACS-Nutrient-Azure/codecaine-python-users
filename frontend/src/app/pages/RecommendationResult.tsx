import { useNavigate } from 'react-router';

export function RecommendationResult() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white">
      {/* Main */}
      <main className="relative overflow-hidden">
        {/* Decorative gradients */}
        <div className="absolute inset-0 pointer-events-none">
          <div 
            className="absolute -top-48 -right-48 w-[620px] h-[620px] opacity-40"
            style={{
              background: 'radial-gradient(circle at 35% 35%, rgba(96,165,250,0.26), rgba(59,130,246,0.10) 45%, rgba(255,255,255,0) 70%)'
            }}
          />
          <div 
            className="absolute -bottom-60 -left-60 w-[560px] h-[560px] opacity-30"
            style={{
              background: 'radial-gradient(circle at 35% 35%, rgba(148,163,184,0.22), rgba(255,255,255,0) 65%)'
            }}
          />
        </div>

        <div className="relative z-10 max-w-6xl mx-auto p-8">
          {/* Topbar */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">
                분석 리포트
              </h1>
              <p className="text-gray-500 text-sm">
                하나의 리포트 안에서 결과를 순서대로 확인할 수 있어요.
              </p>
            </div>

            <div className="flex items-center gap-3 px-4 py-3 rounded-full border border-gray-200 bg-white/85 shadow-lg">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-gray-300 to-gray-400" />
              <div className="flex flex-col gap-0.5">
                <b className="text-sm text-gray-900">hong1234@email.com</b>
                <span className="text-xs text-gray-500">마지막 분석: 2026-02-27</span>
              </div>
            </div>
          </div>

          {/* Report Card */}
          <article className="bg-white/92 rounded-[22px] border border-gray-200 shadow-2xl overflow-hidden">
            {/* Header */}
            <header className="px-6 py-5 flex items-start justify-between gap-4 border-b border-gray-100 bg-gradient-to-b from-blue-50/60 to-white/94">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                  건강 상태 분석 보고서
                </h2>
                <p className="text-sm text-gray-600 leading-relaxed">
                  건강검진(CODEF) + 문진 + 현재 복용 영양제 정보를 종합해
                  부족 영양군과 추천 제품을 제안합니다.
                </p>
              </div>
              <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-blue-100/80 border border-blue-200/60 text-blue-700 font-bold text-xs whitespace-nowrap">
                리포트 ID • RPT-20260227
              </div>
            </header>

            <div className="divide-y divide-gray-100">
              {/* Section 1: Health Check */}
              <section className="px-6 py-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-gray-900">
                    1) 건강검진 결과 (CODEF)
                  </h3>
                  <span className="text-xs text-gray-500">원문 항목을 한 섹션에서 확인</span>
                </div>

                <div className="bg-white/90 border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-50/50 border-b border-gray-200">
                        <th className="text-left text-gray-700 font-bold px-4 py-3 w-[22%]">항목</th>
                        <th className="text-left text-gray-700 font-bold px-4 py-3 w-[38%]">결과</th>
                        <th className="text-left text-gray-700 font-bold px-4 py-3 w-[18%]">참고치/기준</th>
                        <th className="text-left text-gray-700 font-bold px-4 py-3">코멘트</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-100">
                        <td className="px-4 py-3 font-medium text-gray-900">검진일</td>
                        <td className="px-4 py-3 text-gray-800">2026-01-18</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">-</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">기관: ○○건강검진센터</td>
                      </tr>
                      <tr className="border-b border-gray-100">
                        <td className="px-4 py-3 font-medium text-gray-900">종합 판정</td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-100 border border-blue-200 text-blue-800 text-xs font-bold">
                            주의 요망
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-500 text-xs">-</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">생활습관 개선 권고</td>
                      </tr>
                      <tr className="border-b border-gray-100">
                        <td className="px-4 py-3 font-medium text-gray-900">문진</td>
                        <td className="px-4 py-3 text-gray-800">수면 부족 · 피로</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">-</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">자가 기입 문진 기반</td>
                      </tr>
                      <tr className="border-b border-gray-100">
                        <td className="px-4 py-3 font-medium text-gray-900">혈압</td>
                        <td className="px-4 py-3 text-gray-800">128 / 86 mmHg</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">정상: &lt; 120/80</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">경계 수준. 염분/수면/운동 점검 권고</td>
                      </tr>
                      <tr className="border-b border-gray-100">
                        <td className="px-4 py-3 font-medium text-gray-900">공복혈당</td>
                        <td className="px-4 py-3 text-gray-800">103 mg/dL</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">정상: 70~99</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">경계. 식습관 조정 권고</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-gray-900">항산화 관련 지표</td>
                        <td className="px-4 py-3 text-gray-800">낮음</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">-</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">식이/보충 필요 가능</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="flex gap-3 mt-4">
                  <button className="px-4 py-3 rounded-2xl border-2 border-blue-200 bg-blue-50 text-blue-700 text-sm font-bold hover:bg-blue-100 transition-colors">
                    원문 상세 보기 ›
                  </button>
                  <button className="px-4 py-3 rounded-2xl border-2 border-blue-200 bg-blue-50 text-blue-700 text-sm font-bold hover:bg-blue-100 transition-colors">
                    데이터 갱신하기 ›
                  </button>
                </div>
              </section>

              {/* Section 2: Need Nutrient */}
              <section className="px-6 py-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-gray-900">
                    2) 부족 영양군 분석 결과
                  </h3>
                  <span className="text-xs text-gray-500">요약 문장으로 근거/주의 포함</span>
                </div>

                <div className="flex gap-4">
                  <div 
                    className="w-14 h-14 flex-shrink-0 rounded-2xl flex items-center justify-center text-2xl border border-blue-200"
                    style={{
                      background: 'radial-gradient(circle at 30% 30%, rgba(96,165,250,0.35), rgba(59,130,246,0.18))',
                      boxShadow: '0 16px 30px rgba(59,130,246,0.10)'
                    }}
                  >
                    💡
                  </div>
                  <div className="flex-1">
                    <p className="text-2xl font-bold text-gray-900 mb-2">
                      비타민 C <span className="text-blue-600">1000mg</span> 필요
                    </p>
                    <p className="text-sm text-gray-600 leading-relaxed mb-4">
                      건강검진(CODEF) 결과와 문진(피로/수면) 및 현재 복용 영양제 정보를 종합하여,
                      부족 영양군과 필요 함량을 산출했습니다.
                    </p>

                    <div className="p-4 rounded-2xl border border-gray-200 bg-gray-50/80 text-sm text-gray-800 leading-relaxed">
                      <div className="mb-3">
                        <span className="font-bold text-gray-600">요약:</span>{' '}
                        현재 등록된 복용 영양제 기준으로 비타민 C 섭취량은{' '}
                        <b className="text-blue-600 font-bold">0mg/day</b>로 추정되며,
                        개인 상태(피로/회복) 및 검진 요약 지표를 반영한 목표 섭취량{' '}
                        <b className="text-blue-600 font-bold">1000mg/day</b> 대비{' '}
                        <b className="text-blue-600 font-bold">부족분 1000mg/day</b>가 계산되었습니다.
                      </div>

                      <ul className="space-y-2 pl-4">
                        <li className="list-disc">
                          <span className="font-bold text-gray-600">계산 근거:</span>{' '}
                          목표 섭취량(개인 상태 기반 권장치) − 현재 추정 섭취량(등록된 복용 영양제 성분/함량 합산)
                        </li>
                        <li className="list-disc">
                          <span className="font-bold text-gray-600">주의 사항:</span>{' '}
                          처방약 복용 중이거나 위장 민감한 경우, 고함량 복용 전 전문가 상담 및 분할 섭취를 권장합니다.
                        </li>
                      </ul>
                    </div>

                    <div className="flex gap-3 mt-4">
                      <button className="px-5 py-3 rounded-2xl bg-gradient-to-b from-blue-400 to-blue-600 text-white font-bold shadow-lg shadow-blue-200 hover:from-blue-500 hover:to-blue-700 transition-all">
                        섭취 계획 세우기 ›
                      </button>
                    </div>
                  </div>
                </div>
              </section>

              {/* Section 3: Products */}
              <section className="px-6 py-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-gray-900">
                    3) 추천 상품
                  </h3>
                  <span className="text-xs text-gray-500">부족분(1000mg) 충족을 목표로 추천</span>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  {[
                    { name: '비타민C 1000mg (정)', meta: '1정/일 • 단일 성분', price: '₩ 12,900' },
                    { name: '비타민C + 아연 콤플렉스', meta: '면역/회복 • 복합', price: '₩ 18,500' },
                    { name: '리포좀 비타민C', meta: '흡수 고려 • 캡슐', price: '₩ 29,000' },
                  ].map((product, idx) => (
                    <div key={idx} className="bg-white/90 rounded-2xl border border-gray-200 shadow-sm p-4 flex flex-col gap-3">
                      <div 
                        className="h-20 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center text-xs font-bold text-gray-400"
                        style={{
                          background: 'radial-gradient(circle at 30% 30%, rgba(226,232,240,0.8), rgba(241,245,249,1))'
                        }}
                      >
                        상품 이미지
                      </div>
                      <p className="text-sm font-bold text-gray-900">{product.name}</p>
                      <div className="text-xs text-gray-500 -mt-2">{product.meta}</div>
                      <div className="flex items-center justify-between mt-auto pt-2">
                        <div className="font-bold text-sm text-gray-900">{product.price}</div>
                        <button className="px-3 py-2 rounded-xl bg-gradient-to-b from-blue-400 to-blue-600 text-white text-xs font-bold hover:from-blue-500 hover:to-blue-700 transition-all">
                          담기
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex gap-3 mt-4">
                  <button className="px-4 py-3 rounded-2xl border-2 border-blue-200 bg-blue-50 text-blue-700 text-sm font-bold hover:bg-blue-100 transition-colors">
                    추천 더 보기 ›
                  </button>
                  <button 
                    onClick={() => navigate('/chatbot')}
                    className="px-4 py-3 rounded-2xl border-2 border-blue-200 bg-blue-50 text-blue-700 text-sm font-bold hover:bg-blue-100 transition-colors"
                  >
                    상담으로 확인 ›
                  </button>
                </div>
              </section>
            </div>
          </article>
        </div>
      </main>
    </div>
  );
}
