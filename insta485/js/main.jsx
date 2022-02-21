import React from 'react';
import ReactDOM from 'react-dom';
import Scroll from './scroll';

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <Scroll url="/api/v1/posts/" />,
  document.getElementById('reactEntry'),
);
