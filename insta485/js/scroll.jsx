import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class InScroll extends React.Component {
  /* Resolve infinite scroll */
  constructor(props) {
    // Initialize immutable
    super(props);
    // mutable items
    this.state = {
      next: '', // next url
      results: [],
      //url: '' // current url
    };
    this.fetchposts = this.fetchposts.bind(this);
  }

  componentDidMount() {
    if (PerformanceNavigationTiming.type === 'back_forward') {
      this.setState({
        next: history.state.next,
        results: history.state.results,
      });
      return;
    }
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          next: data.next,
          results: data.results,
        });
      })
      .catch((error) => console.log(error));
      history.pushState(this.state, '')
  }

  fetchposts() {
    const { next, results } = this.state;
    fetch(next, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          next: data.next,
          results: results.concat(data.results)
        });
      })
      .catch((error) => console.log(error));
      history.pushState(this.state, '')
  }

  render() {
    // user has navigated back
    const { results, next } = this.state;
    console.log('url from parent is', results.url);
    return (
      <div className="Scroll">
        <InfiniteScroll
          dataLength={results.length}
          next={this.fetchposts}
          hasMore={next != ''}
          loader={<h4>Loading...</h4>}
        >
          {results.map((result) => ( // missing key
            <Post key={result.postid.toString()} postid={result.postid} url={result.url} />
          ))}
        </InfiniteScroll>
      </div>
    );
  }
}

InScroll.propTypes = {
  url: PropTypes.string.isRequired,
};

export default InScroll;
