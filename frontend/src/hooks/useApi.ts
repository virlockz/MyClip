import { Scene } from '../types';

const API = '/api';

export async function fetchScenes(episode?: string): Promise<Scene[]> {
  const params = episode ? `?episode=${episode}` : '';
  const res = await fetch(`${API}/scenes${params}`);
  const data = await res.json();
  return data.scenes;
}

export async function searchScenes(query: string, limit = 10): Promise<Scene[]> {
  const res = await fetch(`${API}/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  const data = await res.json();
  return data.results;
}

export async function exportScenes(episode: string, scenes: number[]): Promise<string[]> {
  const res = await fetch(`${API}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ episode, scenes }),
  });
  const data = await res.json();
  return data.exported;
}
