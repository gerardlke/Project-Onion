const TOPIC_COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];


/**
 * Returns a stable color for a topic name, derived from its position in the
 * known topics list. Falls back to the first color if the topic isn't found.
 *
 * @param {string} topicName
 * @param {Array<{name: string}>} topics
 * @
 */
export function getTopicColor(topicName, topics) {
  const index = topics.findIndex((t) => t.name === topicName);
  return TOPIC_COLORS[(index < 0 ? 0 : index) % TOPIC_COLORS.length];
}


/**
 * Builds a renderable scene node from a concept returned by the upload API.
 * Position comes from the backend (post-PCA coordinates); color is derived
 * from which topic the concept belongs to.
 *
 * @param {{ id: string, label: string, x: number, y: number, z: number, topic_name: string }} concept
 * @param {string} color - Pre-resolved topic color.
 * @returns {{ id: string, position: [number, number, number], color: string, label: string, topicName: string }}
 */
export function createConceptNode(concept, color) {
  return {
    id: concept.id,
    position: [concept.x, concept.y, concept.z],
    color,
    label: concept.label,
    topicName: concept.topic_name,
  };
}