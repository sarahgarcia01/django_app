// scripts.js
function isSearchBarEmpty() {
    var searchInput = document.getElementById('searchBar');
    if (searchInput.value.trim() === '') {
      console.log('Search bar is empty');
      return true;
    } else {
      console.log('Search bar has input');
      return false;
    }
  }
  