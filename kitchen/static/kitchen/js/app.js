function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.delete-ingredient-btn');

    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const itemId = this.dataset.id;
            const url = this.dataset.url;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.success) {
                    const row = document.getElementById(`ingredient-row-${itemId}`);
                    if (row) {
                        row.remove();
                    }
                } else {
                    alert(data.message || 'Delete failed.');
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
                alert('Something went wrong.');
            });
        });
    });

    const markCookedButton = document.querySelector('.mark-cooked-btn');
    const cookStatusMessage = document.getElementById('cook-status-message');

    if (markCookedButton) {
        markCookedButton.addEventListener('click', function () {
            const url = this.dataset.url;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.success) {
                    if (cookStatusMessage) {
                        cookStatusMessage.textContent = data.message || 'Recipe marked as cooked.';
                    }
                } else {
                    if (cookStatusMessage) {
                        cookStatusMessage.textContent = data.message || 'Action failed.';
                    }
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
                if (cookStatusMessage) {
                    cookStatusMessage.textContent = 'Something went wrong.';
                }
            });
        });
    }
});