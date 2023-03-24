import React from 'react';

class Bar extends React.Component {
  render() {
    return (
      <div>
        <button className='relevance_button' onClick={() => {
          if (window.relevance) {
            window.relevance.show();
          }
        }}>Search or ask</button>
      </div>
    );
  }
}

export default function SearchBarWrapper(props) {
  return (
    <>
      <Bar {...props} />
    </>
  );
}
