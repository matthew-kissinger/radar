document.addEventListener('DOMContentLoaded', function () {
    let taskInputElement = document.getElementById('task');
    let actionInputElement = document.getElementById('action');
    const processButtonElement = document.getElementById('processButton');
    const clearButtonElement = document.getElementById('clearButton'); 

    function setActionAccordingToTask() {
        if(taskInputElement.value === ""){
            actionInputElement.value = 'start';
        } else {
            actionInputElement.value = 'next';
        }
        showLoadingSpinner();
    }

    function showLoadingSpinner() {
        let loadingOverlayElement = document.getElementById('loadingOverlay');
        loadingOverlayElement.style.display = 'flex';
    }

    function navigateToClearSession() {
        window.location.href = '/clear';
    }

    processButtonElement.addEventListener('click', setActionAccordingToTask);
    clearButtonElement.addEventListener('click', navigateToClearSession);
});
