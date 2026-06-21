const TOPIC_COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

/**
 * Builds a universe node from a topic returned by the upload API.
 *
 * @param {{name: string, description: string}} topic - Topic API object.
 * @param {number} index - Position index in the topic list.
 * @returns {{id: string, position: [number, number, number], color: string, label: string, info: string, topicName: string}}
 */
export function createTopicNode(topic, index) {
  const angle = index * 1.9;
  const radius = 2.4;

  return {
    id: topic.name,
    position: [
      Math.cos(angle) * radius,
      Math.sin(index * 1.3) * 1.2,
      Math.sin(angle) * radius,
    ],
    color: TOPIC_COLORS[index % TOPIC_COLORS.length],
    label: topic.name,
    info: topic.description || 'No description yet.',
    topicName: topic.name,
  };
}
