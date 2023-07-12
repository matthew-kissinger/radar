function setAction() {
    var taskValue = document.getElementById('task').value;
    if(taskValue === ""){
        document.getElementById('action').value='start';
    } else {
        document.getElementById('action').value='next';
    }
    displayLoadingSpinner();
  }

  function clearSession() {
    location.href = '/clear';
  }

  function displayLoadingSpinner() {
    var loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'flex';
  }