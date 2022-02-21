import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
  constructor(props) {
    super(props);
    const { comments } = this.props;
    const { postid } = this.props;
    this.state = {
      commentsState: comments,
      postID: postid,
      value: '',
    };
  }

  // value is the input_text from the user

  componentDidMount() {
    // const { url } = this.props;
    // const {  } = this.props;
    const { postid } = this.props;
    // const { comments } = this.props;
    const url = `/api/v1/posts/${postid}/`;
    // this.setState({ commentsState: comments });
    // Call REST API to get the post's information
    console.log('url', url);
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // return response.json();
      })
      .then((data) => {
        this.setState({
          commentsState: data.comments,
          value: '',
        });
        const { commentsState } = this.state;
        console.log('Comments', commentsState);
      })
      .catch((error) => console.log(error));
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  // DELETE /api/v1 / comments / <commentid>/
  handleDelete(commentid) {
    const cururl = `/api/v1/comments/${commentid}/`;
    fetch(cururl, { credentials: 'same-origin', method: 'DELETE', headers: { 'Content-Type': 'application/json' } })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // return response.json();
      })
      .then(() => {
        console.log('deleting comment');
        this.setState((prevState) => ({
          commentsState: prevState.commentsState.splice((comment) => comment.commentid
            !== commentid),
        }));
      })
      .catch((error) => console.log(error));
  }

  handleEnter(event) {
    // POST /api/v1/comments/?postid=<postid>
    event.preventDefault();
    const { postid } = this.props;
    // const inputComment = event.target.inputComment.value;
    const cururl = `/api/v1/comments/?postid=${postid}`;
    const { value } = this.state;
    fetch(cururl, {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: value }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          commentsState: prevState.commentsState.concat(data),
          value: '',
        }));
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { comments } = this.props;
    const { value } = this.state;
    const { commentsState } = this.state;
    return (
      <div className="commentContent">
        {/* {console.log(comments)} */}
        {comments.map((item) => (
          <p key={item.commentid}>
            <a href={item.ownerShowUrl}>{item.owner}</a>
            {item.text}
            {item.lognameOwnsThis ? (<button type="button" className="delete-comment-button" onClick={this.handleDelete.bind(this, item.commentid)}> Delete comment </button>) : null}
          </p>
        ))}
        {commentsState.map((item) => (
          <p key={item.commentid}>
            <a href={item.ownerShowUrl}>{item.owner}</a>
            {item.text}
            {item.lognameOwnsThis ? (<button type="button" className="delete-comment-button" onClick={this.handleDelete.bind(this, item.commentid)}> Delete comment </button>) : null}
          </p>
        ))}
        <form className="comment-form" onSubmit={this.handleEnter.bind(this)}>
          <input type="text" name="inputComment" value={value} placeholder="Input comments" onChange={this.handleChange.bind(this)} />
        </form>
      </div>
    );
  }
}

Comments.propTypes = {
  comments: PropTypes.arrayOf(
    PropTypes.shape({
      commentid: PropTypes.number.isRequired,
      lognameOwnsThis: PropTypes.bool.isRequired,
      owner: PropTypes.string.isRequired,
      ownerShowUrl: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
    }),
  ).isRequired,
  postid: PropTypes.number.isRequired,
  url: PropTypes.string.isRequired,
};

export default Comments;
