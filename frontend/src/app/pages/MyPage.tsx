import { useState, useEffect } from 'react';
import { ChevronLeft, Bell, Share2, MoreVertical, X, Plus, ScanLine } from 'lucide-react';
import { Switch } from '../components/ui/switch';
import { api, setToken, setCognitoId, getCognitoId, clearAuth } from '../api';

const DEV_COGNITO_ID = 'test-user-001';

interface Supplement {
  ans_current_id: number;
  ans_product_name: string | null;
  ans_serving_amount: number | null;
  ans_serving_per_day: number | null;
  ans_daily_total_amount: number | null;
  ans_is_active: boolean | null;
  ans_ingredients: Record<string, number> | null;
}

interface Profile {
  cognito_id: string;
  email: string;
  ans_birth_dt: string | null;
  ans_gender: number | null;
  ans_height: number | null;
  ans_weight: number | null;
  ans_allergies: string | null;
  ans_chron_diseases: string | null;
  ans_current_conditions: string | null;
}

const ICONS = ['🟠', '🟡', '🟢', '🔵', '🟣'];

async function fetchDevToken(): Promise<string> {
  const tokenData = await api.getDevToken(DEV_COGNITO_ID);
  setToken(tokenData.access_token);
  setCognitoId(DEV_COGNITO_ID);
  return DEV_COGNITO_ID;
}

export function MyPage() {
  const [supplements, setSupplements] = useState<Supplement[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedSupplement, setSelectedSupplement] = useState<number | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'inactive'>('all');

  const [isEditingUser, setIsEditingUser] = useState(false);
  const [isAddingAllergy, setIsAddingAllergy] = useState(false);
  const [isAddingCondition, setIsAddingCondition] = useState(false);

  const [newAllergy, setNewAllergy] = useState('');
  const [newCondition, setNewCondition] = useState('');

  const [editedUserInfo, setEditedUserInfo] = useState({
    ans_birth_dt: '',
    ans_gender: '',
    ans_weight: '',
    ans_height: '',
  });

  async function loadData(cognitoId: string) {
    const [profileData, supplementsData] = await Promise.all([
      api.getProfile(cognitoId),
      api.getSupplements(cognitoId),
    ]);
    setProfile(profileData);
    setSupplements(supplementsData.supplements ?? []);
    setEditedUserInfo({
      ans_birth_dt: profileData.ans_birth_dt || '',
      ans_gender: profileData.ans_gender !== null ? String(profileData.ans_gender) : '',
      ans_weight: profileData.ans_weight?.toString() || '',
      ans_height: profileData.ans_height?.toString() || '',
    });
  }

  useEffect(() => {
    async function init() {
      try {
        let cognitoId = getCognitoId();
        if (!cognitoId) {
          cognitoId = await fetchDevToken();
        }
        await loadData(cognitoId);
      } catch (e: any) {
        if (e.message === '401') {
          // 토큰 만료 시 재발급 후 재시도
          try {
            const cognitoId = await fetchDevToken();
            await loadData(cognitoId);
          } catch (retryErr: any) {
            setError(retryErr.message);
          }
        } else {
          setError(e.message);
        }
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const toggleSupplement = async (id: number, currentActive: boolean) => {
    try {
      const updated = await api.toggleSupplementStatus(id, !currentActive);
      setSupplements(supplements.map(s =>
        s.ans_current_id === id ? { ...s, ans_is_active: updated.ans_is_active } : s
      ));
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleSupplementClick = (id: number) => {
    setSelectedSupplement(selectedSupplement === id ? null : id);
  };

  const allergiesList = profile?.ans_allergies
    ? profile.ans_allergies.split(',').map(a => a.trim()).filter(Boolean)
    : [];

  const conditionsList = profile?.ans_chron_diseases
    ? profile.ans_chron_diseases.split(',').map(c => c.trim()).filter(Boolean)
    : [];

  const removeAllergy = async (allergy: string) => {
    if (!profile) return;
    const updated = allergiesList.filter(a => a !== allergy).join(', ');
    await api.updateProfile(profile.cognito_id, { ans_allergies: updated });
    const refreshed = await api.getProfile(profile.cognito_id);
    setProfile(refreshed);
  };

  const removeCondition = async (condition: string) => {
    if (!profile) return;
    const updated = conditionsList.filter(c => c !== condition).join(', ');
    await api.updateProfile(profile.cognito_id, { ans_chron_diseases: updated });
    const refreshed = await api.getProfile(profile.cognito_id);
    setProfile(refreshed);
  };

  const handleAddAllergy = async () => {
    if (!newAllergy.trim() || !profile) return;
    const updated = [...allergiesList, newAllergy.trim()].join(', ');
    await api.updateProfile(profile.cognito_id, { ans_allergies: updated });
    const refreshed = await api.getProfile(profile.cognito_id);
    setProfile(refreshed);
    setNewAllergy('');
    setIsAddingAllergy(false);
  };

  const handleAddCondition = async () => {
    if (!newCondition.trim() || !profile) return;
    const updated = [...conditionsList, newCondition.trim()].join(', ');
    await api.updateProfile(profile.cognito_id, { ans_chron_diseases: updated });
    const refreshed = await api.getProfile(profile.cognito_id);
    setProfile(refreshed);
    setNewCondition('');
    setIsAddingCondition(false);
  };

  const handleSaveUserInfo = async () => {
    if (!profile) return;
    const data: any = {};
    if (editedUserInfo.ans_birth_dt) data.ans_birth_dt = editedUserInfo.ans_birth_dt;
    if (editedUserInfo.ans_gender !== '') data.ans_gender = parseInt(editedUserInfo.ans_gender);
    if (editedUserInfo.ans_weight) data.ans_weight = parseFloat(editedUserInfo.ans_weight);
    if (editedUserInfo.ans_height) data.ans_height = parseFloat(editedUserInfo.ans_height);

    try {
      await api.updateProfile(profile.cognito_id, data);
      const refreshed = await api.getProfile(profile.cognito_id);
      setProfile(refreshed);
      setIsEditingUser(false);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleCancelEditUser = () => {
    if (profile) {
      setEditedUserInfo({
        ans_birth_dt: profile.ans_birth_dt || '',
        ans_gender: profile.ans_gender !== null ? String(profile.ans_gender) : '',
        ans_weight: profile.ans_weight?.toString() || '',
        ans_height: profile.ans_height?.toString() || '',
      });
    }
    setIsEditingUser(false);
  };

  const filteredSupplements = supplements.filter(s => {
    if (filter === 'active') return s.ans_is_active;
    if (filter === 'inactive') return !s.ans_is_active;
    return true;
  });

  const selected = supplements.find(s => s.ans_current_id === selectedSupplement);

  const genderDisplay = profile?.ans_gender === 0 ? '남성' : profile?.ans_gender === 1 ? '여성' : '-';

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500 text-lg">로딩 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 text-lg mb-2">오류 발생</p>
          <p className="text-gray-600">{error}</p>
          <button
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg"
            onClick={() => { clearAuth(); window.location.reload(); }}
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">내 정보 관리</h1>
          <div className="flex items-center gap-3">
            <button className="p-2 hover:bg-gray-100 rounded-lg"><Bell className="w-5 h-5 text-gray-600" /></button>
            <button className="p-2 hover:bg-gray-100 rounded-lg"><Share2 className="w-5 h-5 text-gray-600" /></button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-2 gap-6">
          {/* Left - Supplement List */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">영양제</h2>
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  {(['all', 'active', 'inactive'] as const).map(f => (
                    <button key={f} onClick={() => setFilter(f)}
                      className={`px-3 py-2 rounded-lg text-sm ${filter === f ? 'bg-blue-500 text-white font-medium' : 'bg-gray-50 border border-gray-200'}`}>
                      {f === 'all' ? '전체' : f === 'active' ? '활성' : '비활성'}
                    </button>
                  ))}
                </div>
                <button className="flex items-center justify-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm hover:bg-gray-100">
                  <ScanLine className="w-4 h-4" /><span>스캔하기</span>
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {filteredSupplements.map((supplement, idx) => (
                <div key={supplement.ans_current_id} onClick={() => handleSupplementClick(supplement.ans_current_id)}
                  className={`border rounded-xl p-4 transition-colors cursor-pointer ${selectedSupplement === supplement.ans_current_id ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-blue-300'}`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
                        {ICONS[idx % ICONS.length]}
                      </div>
                      <h3 className="font-medium text-gray-900">{supplement.ans_product_name}</h3>
                    </div>
                    <div className="flex items-center gap-3">
                      <div onClick={(e) => e.stopPropagation()}>
                        <Switch checked={supplement.ans_is_active ?? false}
                          onCheckedChange={() => toggleSupplement(supplement.ans_current_id, supplement.ans_is_active ?? false)} />
                      </div>
                      <button className="text-gray-400 hover:text-gray-600" onClick={(e) => e.stopPropagation()}>
                        <MoreVertical className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>1일 복용량: {supplement.ans_daily_total_amount ?? '-'}알</p>
                    <p>1일 {supplement.ans_serving_per_day ?? '-'}회 (1회 {supplement.ans_serving_amount ?? '-'}알)</p>
                  </div>
                </div>
              ))}
              {filteredSupplements.length === 0 && <p className="text-center text-gray-400 py-8">영양제가 없습니다.</p>}
            </div>
          </div>

          {/* Right Panel */}
          {selectedSupplement && selected ? (
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center gap-3 mb-6">
                <button className="p-2 hover:bg-gray-100 rounded-lg" onClick={() => setSelectedSupplement(null)}>
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <h2 className="text-xl font-bold text-gray-900">{selected.ans_product_name}</h2>
              </div>
              <div className="space-y-4">
                {[
                  ['1일 복용량', `${selected.ans_daily_total_amount ?? '-'}알`],
                  ['복용 횟수', `1일 ${selected.ans_serving_per_day ?? '-'}회`],
                  ['1회 복용량', `${selected.ans_serving_amount ?? '-'}알`],
                  ['상태', selected.ans_is_active ? '복용중' : '중단'],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">{label}</span>
                    <span className={`font-medium ${label === '상태' && selected.ans_is_active ? 'text-green-600' : label === '상태' ? 'text-gray-400' : 'text-gray-900'}`}>{value}</span>
                  </div>
                ))}
                {selected.ans_ingredients && Object.keys(selected.ans_ingredients).length > 0 && (
                  <div className="py-3 border-b border-gray-100">
                    <span className="text-gray-600">주요 성분</span>
                    <div className="mt-2 space-y-1">
                      {Object.entries(selected.ans_ingredients).map(([name, amount]) => (
                        <p key={name} className="text-sm text-gray-700">{name}: {amount}mg</p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* User Info */}
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">유저 정보</h2>
                  <button className="text-blue-500 text-sm font-medium hover:text-blue-600" onClick={() => setIsEditingUser(true)}>수정</button>
                </div>
                <div className="space-y-4">
                  {[
                    { label: '이메일', value: profile?.email, editKey: null },
                    { label: '생년월일', value: profile?.ans_birth_dt, editKey: 'ans_birth_dt' },
                    { label: '성별', value: genderDisplay, editKey: 'ans_gender' },
                    { label: '체중', value: profile?.ans_weight ? `${profile.ans_weight} kg` : '-', editKey: 'ans_weight' },
                    { label: '키', value: profile?.ans_height ? `${profile.ans_height} cm` : '-', editKey: 'ans_height' },
                  ].map(item => (
                    <div key={item.label} className="flex items-center gap-2">
                      <span className="text-gray-600 w-20">• {item.label}</span>
                      {isEditingUser && item.editKey ? (
                        <input
                          type={item.editKey === 'ans_gender' ? 'number' : 'text'}
                          value={editedUserInfo[item.editKey as keyof typeof editedUserInfo]}
                          onChange={(e) => setEditedUserInfo({ ...editedUserInfo, [item.editKey!]: e.target.value })}
                          placeholder={item.editKey === 'ans_gender' ? '0=남성 1=여성' : ''}
                          className="border border-gray-300 px-2 py-1 rounded flex-1"
                        />
                      ) : (
                        <span className="text-gray-900">{item.value || '-'}</span>
                      )}
                    </div>
                  ))}
                </div>
                {isEditingUser && (
                  <div className="flex items-center justify-end mt-4 gap-2">
                    <button className="text-gray-500 hover:text-gray-700" onClick={handleCancelEditUser}>취소</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" onClick={handleSaveUserInfo}>저장</button>
                  </div>
                )}
              </div>

              {/* Allergy */}
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-gray-900">알러지 정보</h2>
                  <button className="text-blue-500 hover:text-blue-600" onClick={() => setIsAddingAllergy(true)}><Plus className="w-5 h-5" /></button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {allergiesList.map((a) => (
                    <div key={a} className="flex items-center gap-2 px-3 py-1.5 bg-red-50 text-red-600 rounded-lg border border-red-200">
                      <span>{a}</span>
                      <button onClick={() => removeAllergy(a)} className="hover:text-red-700"><X className="w-4 h-4" /></button>
                    </div>
                  ))}
                  {allergiesList.length === 0 && <p className="text-gray-400 text-sm">등록된 알러지가 없습니다.</p>}
                </div>
                {isAddingAllergy && (
                  <div className="mt-4 flex gap-2">
                    <input type="text" value={newAllergy} onChange={(e) => setNewAllergy(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddAllergy()}
                      className="border border-gray-300 px-2 py-1 rounded flex-1" placeholder="알러지 추가" autoFocus />
                    <button className="text-gray-500 hover:text-gray-700" onClick={() => { setIsAddingAllergy(false); setNewAllergy(''); }}>취소</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" onClick={handleAddAllergy}>추가</button>
                  </div>
                )}
              </div>

              {/* Conditions */}
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-gray-900">기저질환 정보</h2>
                  <button className="text-blue-500 hover:text-blue-600" onClick={() => setIsAddingCondition(true)}><Plus className="w-5 h-5" /></button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {conditionsList.map((c) => (
                    <div key={c} className="flex items-center gap-2 px-3 py-1.5 bg-orange-50 text-orange-600 rounded-lg border border-orange-200">
                      <span>{c}</span>
                      <button onClick={() => removeCondition(c)} className="hover:text-orange-700"><X className="w-4 h-4" /></button>
                    </div>
                  ))}
                  {conditionsList.length === 0 && <p className="text-gray-400 text-sm">등록된 기저질환이 없습니다.</p>}
                </div>
                {isAddingCondition && (
                  <div className="mt-4 flex gap-2">
                    <input type="text" value={newCondition} onChange={(e) => setNewCondition(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddCondition()}
                      className="border border-gray-300 px-2 py-1 rounded flex-1" placeholder="기저질환 추가" autoFocus />
                    <button className="text-gray-500 hover:text-gray-700" onClick={() => { setIsAddingCondition(false); setNewCondition(''); }}>취소</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" onClick={handleAddCondition}>추가</button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
