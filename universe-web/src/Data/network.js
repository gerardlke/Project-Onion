import { apiFetch } from '../Api';


// Getting topic color for the concept node
const TOPIC_COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

export function getTopicColor(topicName, topics) {
  const index = topics.findIndex((t) => t.name === topicName);
  console.log('TOPIC COLOR:', TOPIC_COLORS[(index < 0 ? 0 : index) % TOPIC_COLORS.length]);
  return TOPIC_COLORS[(index < 0 ? 0 : index) % TOPIC_COLORS.length];
}

// Creating the concept node in the network
export async function createConceptNode(concept, color) {

  const nodeResponse = await apiFetch(`/universe/node/${concept.id}`);
  if (!nodeResponse.ok) throw new Error('Failure while pulling concept node data');
  const nodeResult = await nodeResponse.json();

  const radius = 0.2 + (nodeResult.text.length * 0.002);
  
  const topicResponse = await apiFetch(`/universe/topic/${concept.topic_id}`);
  if (!topicResponse.ok) throw new Error('Failure while pulling topic details');
  const topicResult = await topicResponse.json();

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