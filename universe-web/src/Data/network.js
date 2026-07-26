import { apiFetch } from '../Api';


// Getting topic color for the concept node
export const TOPIC_COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

export function getTopicColor(topicId) {
  return TOPIC_COLORS[(topicId < 0 ? 0 : topicId) % TOPIC_COLORS.length];
}


export async function createConceptNode(concept, color) {
  const radius = 0.2 + ((concept.text_length ?? 0) * 0.002);
  return {
    id: concept.id,
    position: concept.coordinates.map((i) => i * 10),
    color,
    radius,
    topicId: concept.topic_id
  };
}

export async function fetchNodeDetail(conceptId) {
  const response = await apiFetch(`/universe/node/${conceptId}`);
  if (!response.ok) throw new Error('Failed to fetch concept detail');
  return response.json();
}
