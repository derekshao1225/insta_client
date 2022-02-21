import React from 'react';
import PropTypes from 'prop-types';
import Moment from 'moment';
import Likes from './likes';
import Comments from './comments';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
     */
  constructor(props) {
    // Initialize immutable
    super(props);
    // mutable items
    this.state = {
      created: '',
      imgUrl: '',
      lognameLikesThis: false,
      numLikes: 0,
      likeUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      postid: 1,
    };
    this.handleClick = this.handleClick.bind(this);
    this.handleDoubleClick = this.handleDoubleClick.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          created: data.created,
          imgUrl: data.imgUrl,
          lognameLikesThis: data.likes.lognameLikesThis,
          numLikes: data.likes.numLikes,
          likeUrl: data.likes.url,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          postid: data.postid,
        });
      })
      .catch((error) => console.log(error));
  }

  handleClick() {
    const {
      lognameLikesThis, numLikes, likeUrl, postid,
    } = this.state;
    // user dislikes
    // console.log('Like url is ', likeUrl);
    // console.log('lognamelikesthis is ', lognameLikesThis);

    if (lognameLikesThis) {
      fetch(likeUrl, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          // return response.json();
        })
        .then(() => {
          this.setState({
            lognameLikesThis: false,
            numLikes: numLikes - 1,
            likeUrl: 'null',
          });
        })
        .catch((error) => console.log(error));
    } else {
      // user likes
      const pUrl = `/api/v1/likes/?postid=${postid}`;
      // console.log('Liking url is ', pUrl);
      fetch(pUrl, { credentials: 'same-origin', method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          console.log('fetched ', data);
          this.setState({
            lognameLikesThis: true,
            numLikes: numLikes + 1,
            likeUrl: data.url,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  handleDoubleClick() {
    const {
      lognameLikesThis, numLikes, postid,
    } = this.state;
    const pUrl = `/api/v1/likes/?postid=${postid}`;
    // user cannot dislike
    if (!lognameLikesThis) {
      fetch(pUrl, { credentials: 'same-origin', method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            lognameLikesThis: true,
            numLikes: numLikes + 1,
            likeUrl: data.url,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      created, imgUrl, lognameLikesThis, numLikes, owner,
      ownerImgUrl, ownerShowUrl, postShowUrl, postid,
    } = this.state;
    const { url } = this.props;
    // Render number of post image and post owner
    // console.log('url for post %d', postid);
    return (
      <div className="post">
        <div>
          <a href={ownerShowUrl}>
            <img src={ownerImgUrl} alt="owner_img_url" className="owner_img" />
          </a>
          <a href={ownerShowUrl}>{owner}</a>
          <a href={postShowUrl}>
            <p>{Moment.utc(created, 'YYYY-MM-DD hh:mm:ss').fromNow()}</p>
          </a>
        </div>
        <div>
          <img src={imgUrl} alt="post_img_url" className="post_img" onDoubleClick={this.handleDoubleClick} />
        </div>
        <div>
          <Likes
            lognameLikesThis={lognameLikesThis}
            numLikes={numLikes}
            onClick={this.handleClick}
          />
          <Comments url={url} postid={postid} />
        </div>
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
