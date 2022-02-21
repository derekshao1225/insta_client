// import React from 'react';
// import PropTypes from 'prop-types';

// function Likes({ lognameLikesThis, numLikes, onClick }) {
//   return (
//     <div>
//       <button type="button" className="like-unlike-button" onClick={onClick}>
//         <p>{lognameLikesThis ? 'unlike' : 'like'}</p>
//       </button>
//       <div className="likes">
//         <p>
//           {numLikes}
//           {' '}
//           like
//           {numLikes !== 1 ? 's' : ''}
//         </p>
//       </div>
//     </div>
//   );
// }

// Likes.propTypes = {
//   lognameLikesThis: PropTypes.string.isRequired,
//   numLikes: PropTypes.number.isRequired,
//   onClick: PropTypes.func.isRequired,
// };
// export default Likes;

// lognameLikesThis = { lognameLikesThis }
// numLikes = { numLikes }
// url = { url }
// onClick = { this.handleClick }

import React from 'react';
import PropTypes from 'prop-types';

class Likes extends React.Component {
  constructor(props) {
    // Initialize mutable state
    super(props);
  }

  render() {
    const { lognameLikesThis, numLikes } = this.props;
    // display number of likes
    return (
      <div>
        <button type="button" className="like-unlike-button" onClick={this.props.onClick}>
          <p>{lognameLikesThis ? 'unlike' : 'like'}</p>
        </button>

        <div className="likes">
          <p>
            {numLikes}
            {' '}
            like
            {numLikes !== 1 ? 's' : ''}
          </p>
        </div>
      </div>
    );
  }
}

Likes.propTypes = {
  lognameLikesThis: PropTypes.bool.isRequired,
  numLikes: PropTypes.number.isRequired,
  onClick: PropTypes.func.isRequired,
};

export default Likes;
