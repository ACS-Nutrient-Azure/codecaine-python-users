import { useState, useRef } from 'react';
import { X, Upload, Camera, Loader2, AlertTriangle, Plus, Trash2 } from 'lucide-react';
import { api, getCognitoId } from '../api';

// 스캔 API 응답 타입
interface ScanResult {
  success: boolean;
  raw_text: string;
  parsed: {
    ans_product_name: string | null;
    ans_serving_amount: number | null;
    ans_serving_per_day: number | null;
    ans_daily_total_amount: number | null;
    ans_ingredients: Record<string, number> | null;
  };
  confidence: {
    product_name: number;
    serving_info: number;
    ingredients: number;
  };
  warnings: string[];
}

// 수정 가능한 폼 타입
interface EditableForm {
  ans_product_name: string;
  ans_serving_amount: string;
  ans_serving_per_day: string;
  ans_daily_total_amount: string;
  ingredients: Array<{ name: string; amount: string }>;
}

type ScanStep = 'upload' | 'loading' | 'review' | 'done';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export function SupplementScanModal({ isOpen, onClose, onSaved }: Props) {
  const [step, setStep] = useState<ScanStep>('upload');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [form, setForm] = useState<EditableForm>({
    ans_product_name: '',
    ans_serving_amount: '',
    ans_serving_per_day: '',
    ans_daily_total_amount: '',
    ingredients: [],
  });
  const [showRawText, setShowRawText] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileSelect = (file: File) => {
    setImageFile(file);
    const url = URL.createObjectURL(file);
    setImagePreview(url);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) handleFileSelect(file);
  };

  const handleAnalyze = async () => {
    if (!imageFile) return;
    setStep('loading');
    try {
      const cognitoId = getCognitoId();
      if (!cognitoId) throw new Error('인증 정보가 없습니다.');
      const result: ScanResult = await api.scanSupplement(imageFile, cognitoId);
      setScanResult(result);
      // 파싱 결과를 폼에 채우기
      setForm({
        ans_product_name: result.parsed.ans_product_name ?? '',
        ans_serving_amount: result.parsed.ans_serving_amount?.toString() ?? '',
        ans_serving_per_day: result.parsed.ans_serving_per_day?.toString() ?? '',
        ans_daily_total_amount: result.parsed.ans_daily_total_amount?.toString() ?? '',
        ingredients: result.parsed.ans_ingredients
          ? Object.entries(result.parsed.ans_ingredients).map(([name, amount]) => ({
              name,
              amount: amount.toString(),
            }))
          : [],
      });
      setStep('review');
    } catch (e: any) {
      alert(`분석 실패: ${e.message}`);
      setStep('upload');
    }
  };

  const handleSave = async () => {
    if (!form.ans_product_name.trim()) {
      alert('제품명을 입력해주세요.');
      return;
    }
    const cognitoId = getCognitoId();
    if (!cognitoId) return;

    setIsSaving(true);
    try {
      const ingredientsObj = form.ingredients.reduce(
        (acc, { name, amount }) => {
          if (name.trim() && amount.trim()) {
            acc[name.trim()] = parseFloat(amount);
          }
          return acc;
        },
        {} as Record<string, number>
      );

      await api.createSupplement({
        cognito_id: cognitoId,
        ans_product_name: form.ans_product_name.trim(),
        ans_serving_amount: form.ans_serving_amount ? parseInt(form.ans_serving_amount) : null,
        ans_serving_per_day: form.ans_serving_per_day ? parseInt(form.ans_serving_per_day) : null,
        ans_daily_total_amount: form.ans_daily_total_amount ? parseInt(form.ans_daily_total_amount) : null,
        ans_is_active: true,
        ans_ingredients: Object.keys(ingredientsObj).length > 0 ? ingredientsObj : null,
      });
      setStep('done');
    } catch (e: any) {
      alert(`저장 실패: ${e.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = () => {
    // 상태 초기화
    setStep('upload');
    setImageFile(null);
    setImagePreview(null);
    setScanResult(null);
    setShowRawText(false);
    if (step === 'done') onSaved();
    else onClose();
  };

  const isLowConfidence = (field: 'product_name' | 'serving_info' | 'ingredients') => {
    return scanResult ? scanResult.confidence[field] < 0.7 : false;
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-900">
            {step === 'upload' && '성분표 스캔'}
            {step === 'loading' && '분석 중...'}
            {step === 'review' && '분석 결과 확인'}
            {step === 'done' && '저장 완료'}
          </h2>
          {step !== 'loading' && (
            <button onClick={handleClose} className="p-2 hover:bg-gray-100 rounded-lg">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          )}
        </div>

        <div className="p-6">
          {/* Step 1: 업로드 */}
          {step === 'upload' && (
            <div className="space-y-4">
              <p className="text-sm text-gray-500">영양제 성분표 부분을 촬영하거나 이미지를 업로드하세요.</p>

              {/* 드래그앤드롭 영역 */}
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                {imagePreview ? (
                  <img src={imagePreview} alt="미리보기" className="max-h-48 mx-auto rounded-lg object-contain" />
                ) : (
                  <>
                    <Upload className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">클릭하거나 이미지를 드래그하여 업로드</p>
                    <p className="text-xs text-gray-400 mt-1">JPEG, PNG, WEBP · 최대 5MB</p>
                  </>
                )}
              </div>

              <div className="flex gap-2">
                <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
                <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleFileChange} />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50"
                >
                  <Upload className="w-4 h-4" /> 파일 선택
                </button>
                <button
                  onClick={() => cameraInputRef.current?.click()}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50"
                >
                  <Camera className="w-4 h-4" /> 카메라 촬영
                </button>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={!imageFile}
                className="w-full py-3 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                분석하기
              </button>
            </div>
          )}

          {/* Step 2: 로딩 */}
          {step === 'loading' && (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
              <p className="text-gray-600 font-medium">성분표를 분석하고 있습니다...</p>
              <p className="text-sm text-gray-400">AWS Textract가 텍스트를 인식 중입니다</p>
            </div>
          )}

          {/* Step 3: 검토 및 수정 */}
          {step === 'review' && scanResult && (
            <div className="space-y-4">
              {/* 경고 메시지 */}
              {scanResult.warnings.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 space-y-1">
                  {scanResult.warnings.map((w, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-yellow-700">
                      <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* 제품명 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  제품명 {isLowConfidence('product_name') && <span className="text-yellow-500 text-xs">· 확인 필요</span>}
                </label>
                <input
                  type="text"
                  value={form.ans_product_name}
                  onChange={(e) => setForm({ ...form, ans_product_name: e.target.value })}
                  className={`w-full border rounded-lg px-3 py-2 text-sm ${isLowConfidence('product_name') ? 'border-yellow-400' : 'border-gray-200'}`}
                  placeholder="제품명 입력"
                />
              </div>

              {/* 복용 정보 */}
              <div className={`grid grid-cols-3 gap-3 p-3 rounded-xl ${isLowConfidence('serving_info') ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'}`}>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">1회 복용량 (알)</label>
                  <input
                    type="number"
                    value={form.ans_serving_amount}
                    onChange={(e) => setForm({ ...form, ans_serving_amount: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm"
                    placeholder="-"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">1일 횟수</label>
                  <input
                    type="number"
                    value={form.ans_serving_per_day}
                    onChange={(e) => setForm({ ...form, ans_serving_per_day: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm"
                    placeholder="-"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">1일 총량 (알)</label>
                  <input
                    type="number"
                    value={form.ans_daily_total_amount}
                    onChange={(e) => setForm({ ...form, ans_daily_total_amount: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm"
                    placeholder="-"
                  />
                </div>
              </div>

              {/* 성분 목록 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    주요 성분 {isLowConfidence('ingredients') && <span className="text-yellow-500 text-xs">· 확인 필요</span>}
                  </label>
                  <button
                    onClick={() => setForm({ ...form, ingredients: [...form.ingredients, { name: '', amount: '' }] })}
                    className="flex items-center gap-1 text-xs text-blue-500 hover:text-blue-600"
                  >
                    <Plus className="w-3 h-3" /> 성분 추가
                  </button>
                </div>
                <div className={`space-y-2 ${isLowConfidence('ingredients') ? 'p-3 bg-yellow-50 rounded-xl border border-yellow-200' : ''}`}>
                  {form.ingredients.map((ing, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <input
                        type="text"
                        value={ing.name}
                        onChange={(e) => {
                          const updated = [...form.ingredients];
                          updated[idx] = { ...updated[idx], name: e.target.value };
                          setForm({ ...form, ingredients: updated });
                        }}
                        className="flex-1 border border-gray-200 rounded-lg px-2 py-1.5 text-sm"
                        placeholder="성분명"
                      />
                      <input
                        type="number"
                        value={ing.amount}
                        onChange={(e) => {
                          const updated = [...form.ingredients];
                          updated[idx] = { ...updated[idx], amount: e.target.value };
                          setForm({ ...form, ingredients: updated });
                        }}
                        className="w-20 border border-gray-200 rounded-lg px-2 py-1.5 text-sm"
                        placeholder="mg"
                      />
                      <button
                        onClick={() => setForm({ ...form, ingredients: form.ingredients.filter((_, i) => i !== idx) })}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  {form.ingredients.length === 0 && (
                    <p className="text-xs text-gray-400 text-center py-2">인식된 성분이 없습니다. 직접 추가해주세요.</p>
                  )}
                </div>
              </div>

              {/* 원본 텍스트 토글 */}
              <button
                onClick={() => setShowRawText(!showRawText)}
                className="text-xs text-gray-400 hover:text-gray-600 underline"
              >
                {showRawText ? '원본 텍스트 숨기기' : '원본 인식 텍스트 보기'}
              </button>
              {showRawText && (
                <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-600 max-h-32 overflow-y-auto whitespace-pre-wrap">
                  {scanResult.raw_text}
                </pre>
              )}

              {/* 저장 버튼 */}
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="w-full py-3 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 disabled:opacity-40 flex items-center justify-center gap-2"
              >
                {isSaving && <Loader2 className="w-4 h-4 animate-spin" />}
                {isSaving ? '저장 중...' : '영양제 등록'}
              </button>
            </div>
          )}

          {/* Step 4: 완료 */}
          {step === 'done' && (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-3xl">✓</span>
              </div>
              <p className="text-gray-800 font-medium">영양제가 등록되었습니다!</p>
              <p className="text-sm text-gray-500">{form.ans_product_name}</p>
              <button
                onClick={handleClose}
                className="w-full py-3 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600"
              >
                확인
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
