/**
 * Builds the first universe node from an uploaded file name.
 *
 * Keeping this as a factory function makes it easier to replace the placeholder
 * metadata with backend-derived concepts later without changing NetworkScene.
 *
 * @param {string} fileName - Name of the file selected by the user.
 * @returns {{id: string, position: [number, number, number], color: string, label: string, info: string}}
 */
export function createUploadedFileNode(fileName) {
  return {
    id: 'uploaded-file',
    position: [0, 0, 0],
    color: '#4f46e5',
    label: fileName || 'Uploaded File',
    info: 'Your uploaded notes are ready to explore.',
  };
}
