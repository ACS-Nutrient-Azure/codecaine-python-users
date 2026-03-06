import { useState, useEffect } from 'react';
import { ChevronLeft, Bell, Share2, MoreVertical, X, Plus, ScanLine } from 'lucide-react';
import { Switch } from '../components/ui/switch';
import { api, setToken, getToken } from '../api';

interface Supplement {
  current_id: number;
  product_name: string;
  serving_amount: number | null;
  serving_per_day: number | null;
  daily_total_amount: number | null;
  total_quantity: number | null;
  is_active: boolean | null;
  purchased_dt: string | null;
  estimated_end_dt: string | null;
  start_dt: string | null;
  end_dt: string | null;
}

interface Profile {
  cognito_id: string;
  email: string;
  name: string | null;
  birth_dt: string | null;
  gender: number | null;
  gender_display: string | null;
  phone: string | null;
  height: number | null;
  weight: number | null;
  allergies: string[];
  chron_diseases: string[];
}

const ICONS = ['🟠', '🟡', '🟢', '🔵', '🟣'];

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
    birth_dt: '',
    gender_display: '',
    phone: '',
    weight: '',
    height: '',
  });

  useEffect(() => {
    async function init() {
      try {
        if (!getToken()) {
          const tokenData = await api.getDevToken('test-user-001');
          setToken(tokenData.access_token);
        }
        const [profileData, supplementsData] = await Promise.all([
          api.getProfile(),
          api.getSupplements(),
        ]);
        setProfile(profileData);
        setSupplements(supplementsData);
        setEditedUserInfo({
          birth_dt: profileData.birth_dt || '',
          gender_display: profileData.gender_display || '',
          phone: profileData.phone || '',
          weight: profileData.weight?.toString() || '',
          height: profileData.height?.toString() || '',
        });
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

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

  const handleSupplementClick = (id: number) => {
    setSelectedSupplement(selectedSupplement === id ? null : id);
  };

  const removeAllergy = async (allergy: string) => {
    if (!profile) return;
    const updated = profile.allergies.filter(a => a !== allergy);
    await api.updateProfile({ allergies: updated });
    setProfile({ ...profile, allergies: updated });
  };

  const removeCondition = async (condition: string) => {
    if (!profile) return;
    const updated = profile.chron_diseases.filter(c => c !== condition);
    await api.updateProfile({ chron_diseases: updated });
    setProfile({ ...profile, chron_diseases: updated });
  };

  const handleAddAllergy = async () => {
    if (!newAllergy.trim() || !profile) return;
    const updated = [...profile.allergies, newAllergy.trim()];
    await api.updateProfile({ allergies: updated });
    setProfile({ ...profile, allergies: updated });
    setNewAllergy('');
    setIsAddingAllergy(false);
  };

  const handleAddCondition = async () => {
    if (!newCondition.trim() || !profile) return;
    const updated = [...profile.chron_diseases, newCondition.trim()];
    await api.updateProfile({ chron_diseases: updated });
    setProfile({ ...profile, chron_diseases: updated });
    setNewCondition('');
    setIsAddingCondition(false);
  };

  const handleSaveUserInfo = async () => {
    if (!profile) return;
    const genderMap: Record<string, number> = { '남성': 0, '여성': 1 };
    const data: any = {
      phone: editedUserInfo.phone || undefined,
      weight: editedUserInfo.weight ? parseFloat(editedUserInfo.weight) : undefined,
      height: editedUserInfo.height ? parseFloat(editedUserInfo.height) : undefined,
    };
    if (editedUserInfo.birth_dt) data.birth_dt = editedUserInfo.birth_dt;
    if (editedUserInfo.gender_display in genderMap) data.gender = genderMap[editedUserInfo.gender_display];

    try {
      const updated = await api.updateProfile(data);
      setProfile(updated);
      setIsEditingUser(false);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleCancelEditUser = () => {
    if (profile) {
      setEditedUserInfo({
        birth_dt: profile.birth_dt || '',
        gender_display: profile.gender_display || '',
        phone: profile.phone || '',
        weight: profile.weight?.toString() || '',
        height: profile.height?.toString() || '',
      });
    }
    setIsEditingUser(false);
  };

  const filteredSupplements = supplements.filter(s => {
    if (filter === 'active') return s.is_active;
    if (filter === 'inactive') return !s.is_active;
    return true;
  });

  const selected = supplements.find(s => s.current_id === selectedSupplement);

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
          <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg" onClick={() => window.location.reload()}>
            새로고침
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
                <div key={supplement.current_id} onClick={() => handleSupplementClick(supplement.current_id)}
                  className={`border rounded-xl p-4 transition-colors cursor-pointer ${selectedSupplement === supplement.current_id ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-blue-300'}`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
                        {ICONS[idx % ICONS.length]}
                      </div>
                      <h3 className="font-medium text-gray-900">{supplement.product_name}</h3>
                    </div>
                    <div className="flex items-center gap-3">
                      <div onClick={(e) => e.stopPropagation()}>
                        <Switch checked={supplement.is_active ?? false}
                          onCheckedChange={() => toggleSupplement(supplement.current_id, supplement.is_active ?? false)} />
                      </div>
                      <button className="text-gray-400 hover:text-gray-600" onClick={(e) => e.stopPropagation()}>
                        <MoreVertical className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>1일 복용량: {supplement.daily_total_amount ?? '-'}알</p>
                    <p>1일 {supplement.serving_per_day ?? '-'}회 (1회 {supplement.serving_amount ?? '-'}알)</p>
                    {supplement.total_quantity && <p className="text-gray-500">총 {supplement.total_quantity}정</p>}
                  </div>
                  {supplement.purchased_dt && (
                    <div className="mt-3"><p className="text-xs text-gray-500">구매일: {supplement.purchased_dt}</p></div>
                  )}
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
                <h2 className="text-xl font-bold text-gray-900">{selected.product_name}</h2>
              </div>
              <div className="space-y-4">
                {[
                  ['1일 복용량', `${selected.daily_total_amount ?? '-'}알`],
                  ['복용 횟수', `1일 ${selected.serving_per_day ?? '-'}회`],
                  ['1회 복용량', `${selected.serving_amount ?? '-'}알`],
                  ['총 수량', `${selected.total_quantity ?? '-'}정`],
                  ['섭취 기간', `${selected.purchased_dt ?? '-'} ~ ${selected.estimated_end_dt ?? '-'}`],
                  ['상태', selected.is_active ? '복용중' : '중단'],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-600">{label}</span>
                    <span className={`font-medium ${label === '상태' && selected.is_active ? 'text-green-600' : label === '상태' ? 'text-gray-400' : 'text-gray-900'}`}>{value}</span>
                  </div>
                ))}
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
                    { label: '생년월일', value: profile?.birth_dt, editKey: 'birth_dt' },
                    { label: '성별', value: profile?.gender_display, editKey: 'gender_display' },
                    { label: '연락처', value: profile?.phone, editKey: 'phone' },
                    { label: '체중', value: profile?.weight ? `${profile.weight} kg` : '-', editKey: 'weight' },
                    { label: '키', value: profile?.height ? `${profile.height} cm` : '-', editKey: 'height' },
                  ].map(item => (
                    <div key={item.editKey} className="flex items-center gap-2">
                      <span className="text-gray-600 w-20">• {item.label}</span>
                      {isEditingUser ? (
                        <input type="text" value={editedUserInfo[item.editKey as keyof typeof editedUserInfo]}
                          onChange={(e) => setEditedUserInfo({ ...editedUserInfo, [item.editKey]: e.target.value })}
                          className="border border-gray-300 px-2 py-1 rounded flex-1" />
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
                  {profile?.allergies.map((a) => (
                    <div key={a} className="flex items-center gap-2 px-3 py-1.5 bg-red-50 text-red-600 rounded-lg border border-red-200">
                      <span>{a}</span>
                      <button onClick={() => removeAllergy(a)} className="hover:text-red-700"><X className="w-4 h-4" /></button>
                    </div>
                  ))}
                  {(!profile?.allergies || profile.allergies.length === 0) && <p className="text-gray-400 text-sm">등록된 알러지가 없습니다.</p>}
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
                  {profile?.chron_diseases.map((c) => (
                    <div key={c} className="flex items-center gap-2 px-3 py-1.5 bg-orange-50 text-orange-600 rounded-lg border border-orange-200">
                      <span>{c}</span>
                      <button onClick={() => removeCondition(c)} className="hover:text-orange-700"><X className="w-4 h-4" /></button>
                    </div>
                  ))}
                  {(!profile?.chron_diseases || profile.chron_diseases.length === 0) && <p className="text-gray-400 text-sm">등록된 기저질환이 없습니다.</p>}
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
