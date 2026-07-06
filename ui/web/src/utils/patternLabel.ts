export function patternDisplayLabel(id: string): string {
  const match = id.match(/^p0?(\d+)$/);
  return match ? `Agent Pattern ${match[1]}` : id;
}
