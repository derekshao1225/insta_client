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
      next: '',
      results: [],
    };
    this.fetchposts = this.fetchposts.bind(this);
  }

  componentDidMount() {
    if (String(window.performance.getEntriesByType('navigation')[0].type) === 'back_forward') {
      this.setState({
        next: window.history.state.next,
        results: window.history.state.results,
      });
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
          results: results.concat(data.results),
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // user has navigated back
    const { results, next } = this.state;
    return (
      <div className="Scroll">
        <InfiniteScroll
          dataLength={results.length}
          next={this.fetchposts}
          hasMore={next !== ''}
          loader={<h4>Loading...</h4>}
        >
          {results.map((result) => (
            <div key={result.postid}>
              <Post url={result.url} />
            </div>
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
