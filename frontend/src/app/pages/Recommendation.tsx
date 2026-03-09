import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router';
import {
  ChevronRight,
  User,
  CheckCircle2,
  Calendar,
  Pencil,
  Trash2,
  Plus,
  ChevronLeft,
} from 'lucide-react';
import { MyPageEditModal } from '../components/MyPageEditModal';

type Step = 'info' | 'consent' | 'health' | 'analyzing';
type ConsentChoice = 'agree' | 'disagree';

/* ─────────────────────────────── Portal Logo ─────────────────────────────── */
function PortalLogo() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center relative overflow-hidden shadow">
        <div className="w-5 h-5 border-2 border-white rounded-full" />
      </div>
      <span className="font-bold text-lg text-gray-900">Portal</span>
    </div>
  );
}

/* ─────────────────────────────── Step Indicator ──────────────────────────── */
function StepIndicator({ current }: { current: 1 | 2 | 3 | 4 }) {
  const steps = ['데이터 동의', '건강정보 입력', '분석 중', '결과'];
  return (
    <div className="flex items-center gap-1">
      {steps.map((label, idx) => {
        const num = idx + 1;
        const isActive = num === current;
        const isDone = num < current;
        return (
          <div key={label} className="flex items-center gap-1">
            <div className="flex items-center gap-1.5">
              <div
                className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : isDone
                    ? 'bg-blue-300 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                {num}
              </div>
              <span
                className={`text-xs font-medium whitespace-nowrap ${
                  isActive ? 'text-blue-700' : isDone ? 'text-blue-400' : 'text-gray-400'
                }`}
              >
                {label}
              </span>
            </div>
            {idx < steps.length - 1 && (
              <ChevronRight className="w-3 h-3 text-gray-300 flex-shrink-0" />
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ──────────────────────────── Step 1 — 정보 확인 ─────────────────────────── */
function StepInfo({
  savedSuccess,
  lastUpdated,
  onConfirm,
  onEditInfo,
}: {
  savedSuccess: boolean;
  lastUpdated: string | null;
  onConfirm: () => void;
  onEditInfo: () => void;
}) {
  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="bg-white rounded-3xl shadow-2xl p-10">
        <div className="mb-8">
          <PortalLogo />
        </div>

        {/* Illustration */}
        <div className="flex justify-center mb-8">
          <div className="relative w-32 h-32">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex flex-col items-center gap-1">
                <div className="w-10 h-10 bg-blue-300 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-blue-700" />
                </div>
                <div className="flex gap-1 mt-1">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-2.5 h-2.5 rounded-full"
                      style={{
                        background:
                          i === 0 ? '#f97316' : i === 1 ? '#fbbf24' : '#60a5fa',
                      }}
                    />
                  ))}
                </div>
                <div className="w-12 h-1.5 bg-blue-200 rounded-full mt-1" />
                <div className="w-8 h-1.5 bg-blue-100 rounded-full" />
              </div>
            </div>
          </div>
        </div>

        <h1
          className="text-gray-900 text-center mb-3"
          style={{ fontSize: '24px', fontWeight: 700 }}
        >
          분석 전, 내 정보를 확인해보세요
        </h1>
        <p className="text-center text-gray-500 mb-2" style={{ fontSize: '14px' }}>
          복용 중인 영양제나 건강 정보가 바뀌었다면
          <br />
          먼저 수정해주세요.
        </p>
        <p className="text-center text-gray-400 mb-8" style={{ fontSize: '12px' }}>
          마지막 업데이트: {lastUpdated ?? '-'}
        </p>

        {savedSuccess && (
          <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-xl px-4 py-3 mb-4">
            <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
            <p className="text-green-700 text-sm">정보가 저장되었습니다.</p>
          </div>
        )}

        <div className="flex flex-col gap-3">
          <button
            onClick={onConfirm}
            className="w-full py-4 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 active:bg-blue-800 transition-all shadow-lg shadow-blue-200 flex items-center justify-center gap-2"
          >
            확인 완료, 분석하기
            <ChevronRight className="w-5 h-5" />
          </button>
          <button
            onClick={onEditInfo}
            className="w-full py-4 bg-white text-gray-700 rounded-xl font-medium border-2 border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all"
          >
            내 정보 수정하기
          </button>
        </div>
      </div>

      <div className="flex items-center justify-center gap-4 mt-6">
        {['영양제 복용 기록', '알러지 정보', '기저질환 정보'].map((label) => (
          <div
            key={label}
            className="px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-full text-gray-600 border border-white/80"
            style={{ fontSize: '12px' }}
          >
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────── Step 2 — 데이터 이용 동의 ──────────────────────── */
function StepConsent({
  choice,
  onChoiceChange,
  onNext,
}: {
  choice: ConsentChoice;
  onChoiceChange: (v: ConsentChoice) => void;
  onNext: () => void;
}) {
  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="bg-white rounded-3xl shadow-2xl p-10">
        <div className="mb-8">
          <PortalLogo />
        </div>

        <h2
          className="text-gray-900 text-center mb-3"
          style={{ fontSize: '22px', fontWeight: 700 }}
        >
          데이터 이용 동의
        </h2>
        <p className="text-center text-gray-500 mb-8" style={{ fontSize: '14px' }}>
          건강 검진 결과와 약물 복용 데이터 조회를 위해
          <br />
          동의를 해주세요.
        </p>

        <div className="space-y-4 mb-10">
          {/* 동의합니다 */}
          <label
            className={`flex items-center gap-3 px-5 py-4 rounded-xl border-2 cursor-pointer transition-all ${
              choice === 'agree'
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div
              className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                choice === 'agree' ? 'border-blue-600 bg-blue-600' : 'border-gray-400'
              }`}
            >
              {choice === 'agree' && (
                <div className="w-2 h-2 rounded-full bg-white" />
              )}
            </div>
            <input
              type="radio"
              className="sr-only"
              checked={choice === 'agree'}
              onChange={() => onChoiceChange('agree')}
            />
            <span
              className={`font-medium ${
                choice === 'agree' ? 'text-blue-700' : 'text-gray-700'
              }`}
            >
              동의합니다
            </span>
          </label>

          {/* 동의하지 않습니다 */}
          <label
            className={`flex items-center gap-3 px-5 py-4 rounded-xl border-2 cursor-pointer transition-all ${
              choice === 'disagree'
                ? 'border-gray-400 bg-gray-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div
              className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                choice === 'disagree' ? 'border-gray-500 bg-gray-500' : 'border-gray-400'
              }`}
            >
              {choice === 'disagree' && (
                <div className="w-2 h-2 rounded-full bg-white" />
              )}
            </div>
            <input
              type="radio"
              className="sr-only"
              checked={choice === 'disagree'}
              onChange={() => onChoiceChange('disagree')}
            />
            <span
              className={`font-medium ${
                choice === 'disagree' ? 'text-gray-700' : 'text-gray-500'
              }`}
            >
              동의하지 않습니다
            </span>
          </label>
        </div>

        {/* 다음 버튼 */}
        <button
          onClick={onNext}
          className={`w-full py-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
            choice === 'agree'
              ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-200'
              : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
          }`}
        >
          다음
          <ChevronRight className="w-5 h-5" />
        </button>

        {choice === 'disagree' && (
          <p className="text-center text-gray-400 mt-3" style={{ fontSize: '12px' }}>
            동의하지 않으면 분석을 진행할 수 없습니다. 이전 화면으로 돌아갑니다.
          </p>
        )}
      </div>
    </div>
  );
}

/* ─────────────────────── Step 3 — 건강정보 입력 ─────────────────────────── */
type ExamItem = {
  id: number;
  name: string;
  value: string;
  unit: string;
  status: '정상' | '부족' | '과잉';
  range: string;
};

type MedItem = {
  id: number;
  name: string;
  dose: string;
  schedule: string;
};

function StepHealth({ onConfirm, onBack }: { onConfirm: () => void; onBack: () => void }) {
  const [gender, setGender] = useState<'male' | 'female' | ''>('');
  const [age, setAge] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [examDate, setExamDate] = useState(new Date().toISOString().split('T')[0]);
  const [note, setNote] = useState('');
  const [examItems, setExamItems] = useState<ExamItem[]>([]);
  const [meds, setMeds] = useState<MedItem[]>([]);
  const [isAddingExam, setIsAddingExam] = useState(false);
  const [isAddingMed, setIsAddingMed] = useState(false);
  const [newExam, setNewExam] = useState({ name: '', value: '', unit: '', range: '' });
  const [newMed, setNewMed] = useState({ name: '', dose: '', schedule: '' });

  useEffect(() => {
    async function loadProfile() {
      try {
        const { api, getCognitoId } = await import('../api');
        const cognitoId = getCognitoId();
        if (!cognitoId) return;
        const profile = await api.getProfile(cognitoId);
        if (profile.ans_gender === 0) setGender('male');
        else if (profile.ans_gender === 1) setGender('female');
        if (profile.ans_height) setHeight(String(profile.ans_height));
        if (profile.ans_weight) setWeight(String(profile.ans_weight));
        if (profile.ans_birth_dt) {
          const birth = new Date(profile.ans_birth_dt);
          const now = new Date();
          setAge(String(now.getFullYear() - birth.getFullYear()));
        }
      } catch (e) {
        console.error('프로필 로딩 실패:', e);
      }
    }
    loadProfile();
  }, []);

  const statusColor = (s: ExamItem['status']) =>
    s === '정상' ? 'text-green-600 bg-green-50' : s === '부족' ? 'text-red-500 bg-red-50' : 'text-orange-500 bg-orange-50';

  const removeExamItem = (id: number) => setExamItems(examItems.filter((e) => e.id !== id));
  const removeMed = (id: number) => setMeds(meds.filter((m) => m.id !== id));

  const handleAddExam = () => {
    if (!newExam.name.trim() || !newExam.value.trim()) return;
    const numVal = parseFloat(newExam.value);
    const [min, max] = newExam.range.split('-').map((v) => parseFloat(v.trim()));
    const status: ExamItem['status'] =
      !isNaN(min) && !isNaN(max)
        ? numVal < min ? '부족' : numVal > max ? '과잉' : '정상'
        : '정상';
    setExamItems([...examItems, { id: Date.now(), ...newExam, status }]);
    setNewExam({ name: '', value: '', unit: '', range: '' });
    setIsAddingExam(false);
  };

  const handleAddMed = () => {
    if (!newMed.name.trim()) return;
    setMeds([...meds, { id: Date.now(), ...newMed }]);
    setNewMed({ name: '', dose: '', schedule: '' });
    setIsAddingMed(false);
  };

  return (
    <div className="w-full max-w-5xl mx-auto">
      {/* Page header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-gray-900 mb-1" style={{ fontSize: '28px', fontWeight: 700 }}>
            건강정보 입력
          </h1>
          <p className="text-gray-500" style={{ fontSize: '14px' }}>
            최근 건강검진 결과와 약물 복용 정보를 확인하고 수정해주세요.
          </p>
        </div>
        <StepIndicator current={2} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left: 최근 건강검진 결과 */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <div className="flex items-center gap-2 mb-5">
            <span className="text-lg">📋</span>
            <h2 className="font-bold text-gray-900">최근 건강검진 결과</h2>
          </div>

          <div className="space-y-4">
            {/* 검진일자 */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 w-20 flex-shrink-0">검진일자</span>
              <div className="flex items-center gap-2 flex-1">
                <input
                  type="date"
                  value={examDate}
                  onChange={(e) => setExamDate(e.target.value)}
                  className="flex-1 border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
                <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
              </div>
            </div>

            {/* 성별 */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 w-20 flex-shrink-0">성별</span>
              <div className="flex gap-4">
                {[{ val: 'male', label: '남성' }, { val: 'female', label: '여성' }].map(
                  ({ val, label }) => (
                    <label key={val} className="flex items-center gap-2 cursor-pointer">
                      <div
                        onClick={() => setGender(val as 'male' | 'female')}
                        className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                          gender === val ? 'border-blue-600 bg-blue-600' : 'border-gray-400'
                        }`}
                      >
                        {gender === val && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                      </div>
                      <span className="text-sm text-gray-700">{label}</span>
                    </label>
                  )
                )}
              </div>
            </div>

            {/* 나이 */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 w-20 flex-shrink-0">나이</span>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  className="w-16 border border-gray-200 rounded-lg px-2 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
                <span className="text-sm text-gray-600">세</span>
              </div>
            </div>

            {/* 키 / 몸무게 */}
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 w-20 flex-shrink-0">키</span>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                  className="w-16 border border-gray-200 rounded-lg px-2 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
                <span className="text-sm text-gray-600">cm</span>
              </div>
              <span className="text-sm text-gray-600 ml-2">몸무게</span>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  className="w-16 border border-gray-200 rounded-lg px-2 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
                <span className="text-sm text-gray-600">kg</span>
              </div>
            </div>
          </div>

          {/* 주요 검사 항목 */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-900" style={{ fontSize: '14px' }}>
                주요 검사 항목
              </h3>
              <button
                onClick={() => setIsAddingExam(true)}
                className="flex items-center gap-1 text-blue-600 text-sm font-medium border border-blue-200 bg-blue-50 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                항목 추가
              </button>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-gray-500 font-medium pb-2">항목</th>
                  <th className="text-left text-gray-500 font-medium pb-2">결과</th>
                  <th className="text-left text-gray-500 font-medium pb-2">기준치</th>
                  <th className="text-gray-500 font-medium pb-2">삭제</th>
                </tr>
              </thead>
              <tbody>
                {examItems.map((item) => (
                  <tr key={item.id} className="border-b border-gray-50">
                    <td className="py-2.5 text-gray-700">{item.name}</td>
                    <td className="py-2.5">
                      <span className="text-gray-900">{item.value} {item.unit}</span>
                      <span className={`ml-2 px-1.5 py-0.5 rounded text-xs font-medium ${statusColor(item.status)}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="py-2.5 text-gray-500">{item.range}</td>
                    <td className="py-2.5 text-center">
                      <button onClick={() => removeExamItem(item.id)} className="text-gray-400 hover:text-red-500 transition-colors">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
                {examItems.length === 0 && !isAddingExam && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-gray-400 text-xs">
                      검진 항목을 추가해주세요
                    </td>
                  </tr>
                )}
                {isAddingExam && (
                  <tr className="border-b border-blue-100 bg-blue-50/30">
                    <td className="py-2 pr-1">
                      <input
                        type="text" placeholder="항목명" value={newExam.name}
                        onChange={(e) => setNewExam({ ...newExam, name: e.target.value })}
                        className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                      />
                    </td>
                    <td className="py-2 px-1">
                      <div className="flex gap-1">
                        <input
                          type="text" placeholder="수치" value={newExam.value}
                          onChange={(e) => setNewExam({ ...newExam, value: e.target.value })}
                          className="w-14 border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                        />
                        <input
                          type="text" placeholder="단위" value={newExam.unit}
                          onChange={(e) => setNewExam({ ...newExam, unit: e.target.value })}
                          className="w-14 border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                        />
                      </div>
                    </td>
                    <td className="py-2 px-1">
                      <input
                        type="text" placeholder="예: 30 - 100" value={newExam.range}
                        onChange={(e) => setNewExam({ ...newExam, range: e.target.value })}
                        className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                      />
                    </td>
                    <td className="py-2 pl-1">
                      <div className="flex gap-1 justify-center">
                        <button onClick={handleAddExam} className="text-blue-500 hover:text-blue-700 text-xs font-medium">추가</button>
                        <button onClick={() => { setIsAddingExam(false); setNewExam({ name: '', value: '', unit: '', range: '' }); }} className="text-gray-400 hover:text-gray-600 text-xs">취소</button>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: 현재 약물 복용 정보 + 기타 */}
        <div className="flex flex-col gap-5">
          <div className="bg-white rounded-2xl shadow-sm p-6 flex-1">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-lg">💊</span>
                <h2 className="font-bold text-gray-900">현재 약물 복용 정보</h2>
              </div>
              <button
                onClick={() => setIsAddingMed(true)}
                className="flex items-center gap-1 text-blue-600 text-sm font-medium border border-blue-200 bg-blue-50 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                약물 추가
              </button>
            </div>

            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-gray-500 font-medium pb-2">약품명</th>
                  <th className="text-left text-gray-500 font-medium pb-2">용량</th>
                  <th className="text-left text-gray-500 font-medium pb-2">복용 주기</th>
                  <th className="text-gray-500 font-medium pb-2">수정</th>
                </tr>
              </thead>
              <tbody>
                {meds.map((med) => (
                  <tr key={med.id} className="border-b border-gray-50">
                    <td className="py-2.5 text-gray-800">{med.name}</td>
                    <td className="py-2.5 text-gray-700">{med.dose}</td>
                    <td className="py-2.5 text-gray-600">{med.schedule}</td>
                    <td className="py-2.5">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => removeMed(med.id)}
                          className="text-gray-400 hover:text-red-500 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {meds.length === 0 && !isAddingMed && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-gray-400 text-xs">
                      복용 중인 약물을 추가해주세요
                    </td>
                  </tr>
                )}
                {isAddingMed && (
                  <tr className="border-b border-blue-100 bg-blue-50/30">
                    <td className="py-2 pr-1">
                      <input
                        type="text" placeholder="약품명" value={newMed.name}
                        onChange={(e) => setNewMed({ ...newMed, name: e.target.value })}
                        className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                      />
                    </td>
                    <td className="py-2 px-1">
                      <input
                        type="text" placeholder="용량" value={newMed.dose}
                        onChange={(e) => setNewMed({ ...newMed, dose: e.target.value })}
                        className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                      />
                    </td>
                    <td className="py-2 px-1">
                      <input
                        type="text" placeholder="예: 1일 1회 (아침)" value={newMed.schedule}
                        onChange={(e) => setNewMed({ ...newMed, schedule: e.target.value })}
                        className="w-full border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                      />
                    </td>
                    <td className="py-2 pl-1">
                      <div className="flex gap-1 justify-center">
                        <button onClick={handleAddMed} className="text-blue-500 hover:text-blue-700 text-xs font-medium">추가</button>
                        <button onClick={() => { setIsAddingMed(false); setNewMed({ name: '', dose: '', schedule: '' }); }} className="text-gray-400 hover:text-gray-600 text-xs">취소</button>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            {/* 기타 독이사항 */}
            <div className="mt-5">
              <h3 className="font-bold text-gray-900 mb-2" style={{ fontSize: '14px' }}>
                기타 독이사항
              </h3>
              <div className="relative">
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value.slice(0, 200))}
                  placeholder="알레르기, 복용 중인 약물 등이 있다면 입력해 주세요."
                  className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
                  rows={4}
                />
                <span className="absolute bottom-3 right-3 text-xs text-gray-400">
                  {note.length}/200
                </span>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl border-2 border-gray-300 text-gray-600 font-medium hover:bg-gray-50 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              이전
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
            >
              <CheckCircle2 className="w-4 h-4" />
              확인
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────── Step 4 — 분석 중 ───────────────────────────────── */
function StepAnalyzing() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      {/* Dotted spinner */}
      <div className="relative w-20 h-20 mb-8">
        {Array.from({ length: 12 }).map((_, i) => {
          const angle = (i * 360) / 12;
          const rad = (angle * Math.PI) / 180;
          const x = 50 + 38 * Math.sin(rad);
          const y = 50 - 38 * Math.cos(rad);
          return (
            <div
              key={i}
              className="absolute w-2.5 h-2.5 rounded-full bg-blue-400"
              style={{
                left: `${x}%`,
                top: `${y}%`,
                transform: 'translate(-50%, -50%)',
                opacity: (i + 1) / 12,
                animation: `spin-dot 1.2s linear infinite`,
                animationDelay: `${(i * 1.2) / 12}s`,
              }}
            />
          );
        })}
      </div>
      <p className="text-gray-600" style={{ fontSize: '18px' }}>
        분석 중입니다...
      </p>
      <style>{`
        @keyframes spin-dot {
          0%   { opacity: 0.15; }
          100% { opacity: 1; }
        }
        @keyframes rotate-dots {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

/* ═══════════════════════════ Main Recommendation ═════════════════════════════ */
export function Recommendation() {
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>('info');
  const [visible, setVisible] = useState(true);
  const [consentChoice, setConsentChoice] = useState<ConsentChoice>('agree');
  const [showModal, setShowModal] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    async function fetchLastUpdated() {
      try {
        const { api, getCognitoId } = await import('../api');
        const cognitoId = getCognitoId();
        if (!cognitoId) return;
        const profile = await api.getProfile(cognitoId);
        if (profile.updated_at) {
          const d = new Date(profile.updated_at);
          setLastUpdated(
            `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
          );
        }
      } catch (e) {
        // 로딩 실패 시 무시
      }
    }
    fetchLastUpdated();
  }, []);

  /* ── fade transition helper ── */
  const fadeTo = (nextStep: Step) => {
    setVisible(false);
    timerRef.current = setTimeout(() => {
      setStep(nextStep);
      setVisible(true);
    }, 300);
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  /* ── step handlers ── */
  const handleInfoConfirm = () => fadeTo('consent');

  const handleConsentNext = () => {
    if (consentChoice === 'agree') {
      fadeTo('health');
    } else {
      // 동의하지 않으면 → 정보 확인 화면으로 복귀
      fadeTo('info');
    }
  };

  const handleHealthConfirm = () => {
    fadeTo('analyzing');
    // 2.5초 후 추천 결과 페이지로 이동
    setTimeout(() => navigate('/recommendation-result'), 2800);
  };

  const handleHealthBack = () => fadeTo('consent');

  /* ── modal ── */
  const handleOpenModal = () => {
    setShowModal(true);
    setSavedSuccess(false);
  };
  const handleModalClose = () => setShowModal(false);
  const handleModalSave = () => {
    setShowModal(false);
    setSavedSuccess(true);
  };

  /* ── background gradient ── */
  const bgGradient =
    step === 'health'
      ? 'from-slate-50 via-blue-50 to-indigo-50'
      : 'from-[#EEF2FF] via-[#E0E7FF] to-[#DBEAFE]';

  return (
    <div
      className={`min-h-screen flex items-center justify-center p-8 relative bg-gradient-to-br ${bgGradient} transition-all duration-500`}
    >
      {/* Decorative blobs */}
      <div className="absolute top-16 right-24 w-64 h-64 bg-blue-200/30 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-16 left-16 w-48 h-48 bg-purple-200/20 rounded-full blur-3xl pointer-events-none" />

      {/* Fade wrapper */}
      <div
        className="relative z-10 w-full flex justify-center transition-all duration-300"
        style={{ opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(8px)' }}
      >
        {step === 'info' && (
          <StepInfo
            savedSuccess={savedSuccess}
            lastUpdated={lastUpdated}
            onConfirm={handleInfoConfirm}
            onEditInfo={handleOpenModal}
          />
        )}

        {step === 'consent' && (
          <StepConsent
            choice={consentChoice}
            onChoiceChange={setConsentChoice}
            onNext={handleConsentNext}
          />
        )}

        {step === 'health' && (
          <StepHealth onConfirm={handleHealthConfirm} onBack={handleHealthBack} />
        )}

        {step === 'analyzing' && <StepAnalyzing />}
      </div>

      {/* MyPage edit modal */}
      <MyPageEditModal
        isOpen={showModal}
        onClose={handleModalClose}
        onSave={handleModalSave}
      />
    </div>
  );
}