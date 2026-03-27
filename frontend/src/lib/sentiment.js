export function normalizeSentimentLabel(label) {
  const value = String(label || '').trim().toLowerCase();
  if (value.startsWith('pos')) return 'Positive';
  if (value.startsWith('neg')) return 'Negative';
  return 'Neutral';
}

export function sentimentBreakdown(items, key = 'sentiment_label') {
  const result = { Positive: 0, Neutral: 0, Negative: 0, total: 0 };

  for (const item of items || []) {
    const label = normalizeSentimentLabel(item?.[key]);
    result[label] += 1;
    result.total += 1;
  }

  return result;
}
