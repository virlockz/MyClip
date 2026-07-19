export interface Scene {
  id: number;
  episode: string;
  season: number;
  episode_num: number;
  scene_number: number;
  start_time: number;
  end_time: number;
  duration: number;
  subtitle_text: string;
  thumbnail_path: string;
  video_path: string;
  yolo_objects: string;
  score?: number;
}
