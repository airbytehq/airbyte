import React from 'react';
import SearchBar from '@theme-original/SearchBar';

export default function SearchBarWrapper(props) {
  return (
    <>
      <div style={{display : 'flex'}}>
        <SearchBar {...props} />
        <button  onClick={() => {
          if (window.relevance) {
            window.relevance.show();
          }
        }} className='relevance_button' >or ask</button>
      </div>
    </>
  );
}
