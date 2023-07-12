window.onload = function() {
    var taskInput = document.getElementById('task');
    var actionInput = document.getElementById('action');
    var processButton = document.getElementById('processButton');
    var clearButton = document.getElementById('clearButton'); // Define the clearButton

    function assignAction() {
        if(taskInput.value === ""){
            actionInput.value='start';
        } else {
            actionInput.value='next';
        }
        displayLoadingSpinner();
    }

    function displayLoadingSpinner() {
        var loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.style.display = 'flex';
    }
  
    function redirectToClearSession() {
        window.location.href = '/clear';
    }

    processButton.addEventListener('click', assignAction);
    clearButton.addEventListener('click', redirectToClearSession);
}
