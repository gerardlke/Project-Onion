import starImage from '../Images/Star.png';

/**
 * Upload success marker.
 *
 * Rendered after the app accepts a file selection. This is separate from the
 * backend response so the user receives immediate visual feedback.
 *
 * @returns {JSX.Element}
 */
function Stars() {
  return (
    <div className="stars">
      <img className="star-image" src={starImage} alt="Star" />
    </div>
  );
}

export default Stars;
