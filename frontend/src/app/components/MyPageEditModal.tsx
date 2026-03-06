import { useState, useEffect } from 'react';
import { X, Plus, ChevronRight, MoreVertical } from 'lucide-react';
import { Switch } from './ui/switch';
import { api } from '../api';

interface MyPageEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
}

interface Supplement {
  current_id: number;
  product_name: string;
  serving_amount: number | null;
  serving_per_day: number | null;
  daily_total_amount: number | null;
  is_active: boolean | null;
}

interface Profile {
  birth_dt: string | null;
  gender_display: string | null;
  phone: string | null;
  weight: number | null;
  height: number | null;
  allergies: string[];
  chron_diseases: string[];
}

const ICONS = ['🟠', '🟡', '🟢', '🔵', '🟣'];

export function MyPageEditModal({ isOpen, onClose, onSave }: MyPageEditModalProps) {
  const [supplements, setSupplements] = useState<Supplement[]>([]);
  const [allergies, setAllergies] = useState<string[]>([]);
  const [conditions, setConditions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const [isAddingAllergy, setIsAddingAllergy] = useState(false);
  const [isAddingCondition, setIsAddingCondition] = useState(false);
  const [newAllergy, setNewAllergy] = useState('');
  const [newCondition, setNewCondition] = useState('');

  const [userInfo, setUserInfo] = useState({
    birthdate: '',
    gender: '',
    phone: '',
    weight: '',
    height: '',
  });

  // 모달이 열릴 때마다 API에서 최신 데이터를 가져옴
  useEffect(() => {
    if (!isOpen) return;
    async function fetchData() {
      setLoading(true);
      try {
        const [profileData, supplementsData] = await Promise.all([
          api.getProfile(),
          api.getSupplements(),
        ]);
        setUserInfo({
          birthdate: profileData.birth_dt || '',
          gender: profileData.gender_display || '',
          phone: profileData.phone || '',
          weight: profileData.weight?.toString() || '',
          height: profileData.height?.toString() || '',
        });
        setAllergies(profileData.allergies || []);
        setConditions(profileData.chron_diseases || []);
        setSupplements(supplementsData);
      } catch (e: any) {
        console.error('데이터 로딩 실패:', e.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [isOpen]);

  const toggleSupplement = async (id: number, currentActive: boolean) => {
    try {
      await api.updateSupplement(id, { is_active: !currentActive });
      setSupplements(supplements.map(s =>
        s.current_id === id ? { ...s, is_active: !currentActive } : s
      ));
    } catch (e: any) {
      alert(e.message);
    }
  };

  const removeAllergy = (a: string) => setAllergies(allergies.filter(x => x !== a));
  const removeCondition = (c: string) => setConditions(conditions.filter(x => x !== c));

  const handleAddAllergy = () => {
    if (newAllergy.trim()) {
      setAllergies([...allergies, newAllergy.trim()]);
      setNewAllergy('');
      setIsAddingAllergy(false);
    }
  };

  const handleAddCondition = () => {
    if (newCondition.trim()) {
      setConditions([...conditions, newCondition.trim()]);
      setNewCondition('');
      setIsAddingCondition(false);
    }
  };

  const handleSave = async () => {
    try {
      const genderMap: Record<string, number> = { '남성': 0, '여성': 1 };
      const data: any = {
        allergies,
        chron_diseases: conditions,
      };
      if (userInfo.phone) data.phone = userInfo.phone;
      if (userInfo.weight) data.weight = parseFloat(userInfo.weight);
      if (userInfo.height) data.height = parseFloat(userInfo.height);
      if (userInfo.birthdate) data.birth_dt = userInfo.birthdate;
      if (userInfo.gender in genderMap) data.gender = genderMap[userInfo.gender];

      await api.updateProfile(data);
      onSave();
    } catch (e: any) {
      alert('저장 실패: ' + e.message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="absolute inset-0 bg-black/40 transition-opacity" onClick={onClose} />

      <div
        className="absolute right-0 top-0 h-full w-full max-w-2xl bg-white shadow-2xl flex flex-col"
        style={{ animation: 'slideInRight 0.3s ease-out' }}
      >
        {/* Header */}
        <div className="bg-blue-600 px-6 py-4 flex items-center justify-between flex-shrink-0">
          <h2 className="text-white font-bold text-lg">내 정보 수정</h2>
          <button onClick={onClose} className="text-white/80 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <p className="text-gray-500">로딩 중...</p>
            </div>
          ) : (
            <>
              {/* 영양제 목록 */}
              <div className="bg-gray-50 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-gray-900">복용 중인 영양제 목록</h3>
                  <button className="flex items-center gap-1 text-blue-600 text-sm font-medium hover:text-blue-700">
                    <Plus className="w-4 h-4" />
                    영양제 추가
                  </button>
                </div>
                <div className="space-y-3">
                  {supplements.map((supplement, idx) => (
                    <div key={supplement.current_id} className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-xl">
                          {ICONS[idx % ICONS.length]}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 text-sm">{supplement.product_name}</p>
                          <p className="text-xs text-gray-500">1일 {supplement.daily_total_amount ?? '-'}알 ({supplement.serving_per_day ?? '-'}회)</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={supplement.is_active ?? false}
                          onCheckedChange={() => toggleSupplement(supplement.current_id, supplement.is_active ?? false)}
                        />
                        <button className="text-gray-400 hover:text-gray-600">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                  {supplements.length === 0 && <p className="text-gray-400 text-sm text-center py-4">등록된 영양제가 없습니다.</p>}
                </div>
              </div>

              {/* 건강 정보 */}
              <div className="bg-gray-50 rounded-2xl p-5">
                <h3 className="font-bold text-gray-900 mb-4">건강 정보</h3>
                <div className="space-y-3">
                  {[
                    { label: '생년월일', key: 'birthdate', type: 'text' },
                    { label: '성별', key: 'gender', type: 'text' },
                    { label: '연락처', key: 'phone', type: 'text' },
                    { label: '체중 (kg)', key: 'weight', type: 'number' },
                    { label: '키 (cm)', key: 'height', type: 'number' },
                  ].map((field) => (
                    <div key={field.key} className="flex items-center gap-3">
                      <label className="text-sm text-gray-600 w-24 flex-shrink-0">{field.label}</label>
                      <input
                        type={field.type}
                        value={userInfo[field.key as keyof typeof userInfo]}
                        onChange={(e) => setUserInfo({ ...userInfo, [field.key]: e.target.value })}
                        className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent bg-white"
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* 알러지 */}
              <div className="bg-gray-50 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold text-gray-900">알러지 정보</h3>
                  <button onClick={() => setIsAddingAllergy(true)} className="text-blue-600 hover:text-blue-700">
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {allergies.map((a) => (
                    <div key={a} className="flex items-center gap-2 px-3 py-1.5 bg-red-50 text-red-600 rounded-lg border border-red-200 text-sm">
                      <span>{a}</span>
                      <button onClick={() => removeAllergy(a)} className="hover:text-red-800"><X className="w-3.5 h-3.5" /></button>
                    </div>
                  ))}
                  {allergies.length === 0 && <p className="text-gray-400 text-sm">등록된 알러지가 없습니다.</p>}
                </div>
                {isAddingAllergy && (
                  <div className="mt-3 flex gap-2">
                    <input type="text" value={newAllergy} onChange={(e) => setNewAllergy(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddAllergy()}
                      className="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                      placeholder="알러지 입력" autoFocus />
                    <button onClick={handleAddAllergy} className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">추가</button>
                    <button onClick={() => { setIsAddingAllergy(false); setNewAllergy(''); }} className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300">취소</button>
                  </div>
                )}
              </div>

              {/* 기저질환 */}
              <div className="bg-gray-50 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold text-gray-900">기저질환 정보</h3>
                  <button onClick={() => setIsAddingCondition(true)} className="text-blue-600 hover:text-blue-700">
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {conditions.map((c) => (
                    <div key={c} className="flex items-center gap-2 px-3 py-1.5 bg-orange-50 text-orange-600 rounded-lg border border-orange-200 text-sm">
                      <span>{c}</span>
                      <button onClick={() => removeCondition(c)} className="hover:text-orange-800"><X className="w-3.5 h-3.5" /></button>
                    </div>
                  ))}
                  {conditions.length === 0 && <p className="text-gray-400 text-sm">등록된 기저질환이 없습니다.</p>}
                </div>
                {isAddingCondition && (
                  <div className="mt-3 flex gap-2">
                    <input type="text" value={newCondition} onChange={(e) => setNewCondition(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddCondition()}
                      className="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                      placeholder="기저질환 입력" autoFocus />
                    <button onClick={handleAddCondition} className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">추가</button>
                    <button onClick={() => { setIsAddingCondition(false); setNewCondition(''); }} className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300">취소</button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 border-t border-gray-200 px-6 py-4 flex gap-3 bg-white">
          <button onClick={onClose} className="flex-1 py-3 rounded-xl border-2 border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors">
            취소
          </button>
          <button onClick={handleSave}
            className="flex-1 py-3 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-blue-200">
            저장하고 돌아가기
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }
      `}</style>
    </div>
  );
}
