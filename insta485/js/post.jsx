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
    super(props); // key, postid, url
    // mutable items
    this.state = {
      comments: [],
      created: '',
      imgUrl: '',
      lognameLikesThis: false,
      numLikes: 0,
      likeUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: ''
    };
    this.handleClick = this.handleClick.bind(this);
    this.handleDoubleClick = this.handleDoubleClick.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    console.log('url is %s', url);
    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: data.comments,
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
          url: data.url
        });
      })
      .catch((error) => console.log(error));

      console.log('from fetch url for post %d', this.state.postid);
      console.log('from fetch num of likes %d', this.state.numLikes);
  }

  handleClick() {
    const {
      lognameLikesThis, numLikes
    } = this.state;
    const { postid } = this.props
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
            url: data.url,
          });
        })
        .catch((error) => console.log(error));
    } else {
      fetch(pUrl, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          this.setState({
            lognameLikesThis: false,
            numLikes: numLikes - 1,
            url: pUrl,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  handleDoubleClick() {
    const {
      lognameLikesThis, numLikes
    } = this.state;
    const { postid } = this.props
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
            url: data.url,
          });
        })
        .catch((error) => console.log(error));
    } else {
      fetch(pUrl, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          this.setState({
            lognameLikesThis: false,
            numLikes: numLikes - 1,
            url: pUrl,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      comments, created, imgUrl, lognameLikesThis, numLikes, likeUrl, owner,
      ownerImgUrl, ownerShowUrl, postShowUrl
    } = this.state;
    const { postid, url } = this.props; // get postid and post url from parent
    // Render number of post image and post owner
    
    return (
      <div className="post">
        <div>
          <a href={ownerShowUrl}>
            <img src={ownerImgUrl} alt="owner_img_url" className="owner_img" />
          </a>
          <a href={ownerShowUrl}>{owner}</a>
        </div>
        <div>
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
            likeUrl={likeUrl}
            onClick={this.handleClick}
            postid={postid}
          />
          <Comments comments={comments} postid={postid} url={url} />
        </div>
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
  postid: PropTypes.number.isRequired,
};

export default Post;
