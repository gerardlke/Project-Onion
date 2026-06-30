import { apiFetch } from '../Api';


// Getting topic color for the concept node
const TOPIC_COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

export function getTopicColor(topicName, topics) {
  const index = topics.findIndex((t) => t.name === topicName);
  console.log('TOPIC COLOR:', TOPIC_COLORS[(index < 0 ? 0 : index) % TOPIC_COLORS.length]);
  return TOPIC_COLORS[(index < 0 ? 0 : index) % TOPIC_COLORS.length];
}


// Creating the concept node in the network
const topicCache = new Map();

function fetchTopicCached(topicId) {
  if (topicCache.has(topicId)) {
    return topicCache.get(topicId);
  }

  const requestPromise = (async () => {
    const response = await apiFetch(`/universe/topic/${topicId}`);
    if (!response.ok) throw new Error('Failure while pulling topic details');
    return response.json();
  })();

  topicCache.set(topicId, requestPromise);
  return requestPromise;
}

export async function createConceptNode(concept, color) {

  const nodeResponse = await apiFetch(`/universe/node/${concept.id}`);
  if (!nodeResponse.ok) throw new Error('Failure while pulling concept node data');
  const nodeResult = await nodeResponse.json();

  const radius = 0.2 + (nodeResult.text.length * 0.002);
  
  const topicResult = await fetchTopicCached(concept.topic_id);

  return {
    id: concept.id,
    position: concept.coordinates.map((i) => i * 10),
    color,
    radius,
    label: nodeResult.concept,
    topicName: topicResult.topic,
    text: nodeResult.text
  };
}