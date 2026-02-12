export const TAG_PATTERNS = {
  crimes: [
    { label: '叛亂', pattern: /(叛亂|懲治叛亂條例)/ },
    { label: '匪諜/通匪', pattern: /(匪諜|通匪|知匪不報|為匪宣傳)/ },
    { label: '參加叛亂組織', pattern: /(參加叛亂組織|加入叛亂組織)/ },
    { label: '閱讀禁書/思想', pattern: /(反動書刊|思想偏狹|閱讀左傾)/ },
    { label: '槍砲彈藥', pattern: /(槍砲|彈藥|刀械)/ }
  ],
  reasons: [
    { label: '疑遭刑求', pattern: /(刑求|不正訊問|非任意性|自白|逼供)/ },
    { label: '證據不足', pattern: /(證據不足|無其他證據|唯一證據|推測之詞)/ },
    { label: '違反憲政秩序', pattern: /(違反自由民主憲政秩序|違憲|大法官解釋)/ },
    { label: '審判瑕疵', pattern: /(未經審判|管轄錯誤|審判程序違法)/ },
    { label: '追訴權消滅', pattern: /(追訴權|時效完成)/ }
  ],
  sentences: [
    { label: '死刑', pattern: /(主文[\s\S]{0,100}死刑|執行死刑|處死刑)/ },
    { label: '無期徒刑', pattern: /(主文[\s\S]{0,100}無期徒刑|處無期徒刑)/ },
    { label: '有期徒刑', pattern: /(主文[\s\S]{0,100}有期徒刑|處有期徒刑)/ },
    { label: '感化/感訓', pattern: /(感化教育|感訓|交付感化)/ },
    { label: '沒收財產', pattern: /(沒收財產|沒收其財產)/ }
  ]
};

export function analyzeText(text: string) {
  const result: { crimes: string[], reasons: string[], sentences: string[] } = {
    crimes: [],
    reasons: [],
    sentences: []
  };

  if (!text) return result;

  Object.entries(TAG_PATTERNS).forEach(([category, patterns]) => {
    patterns.forEach(p => {
      if (p.pattern.test(text)) {
        (result as any)[category].push(p.label);
      }
    });
  });

  return result;
}
