function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

function showGlobalMessage(message, type = 'success') {
    const container = document.getElementById('global-status-message');
    if (!container) return;

    container.innerHTML = `
        <div class="alert alert-${type} rounded-4 shadow-sm mb-2" role="status">
            ${message}
        </div>
    `;
}

function updateInventoryCount() {
    const ingredientElements = document.querySelectorAll('[data-ingredient-id]');
    const uniqueIds = new Set(
        Array.from(ingredientElements).map(function (element) {
            return element.dataset.ingredientId;
        })
    );

    const countBadge = document.getElementById('inventory-count-badge');
    if (countBadge) {
        countBadge.textContent = `Total items: ${uniqueIds.size}`;
    }

    const desktopBody = document.getElementById('inventory-table-body');
    const mobileList = document.getElementById('inventory-mobile-list');

    if (uniqueIds.size === 0) {
        if (desktopBody) {
            desktopBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">No ingredients in inventory.</td>
                </tr>
            `;
        }

        if (mobileList) {
            mobileList.innerHTML = `
                <div class="text-center text-muted py-4">No ingredients in inventory.</div>
            `;
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    updateInventoryCount();

    document.addEventListener('click', function (event) {
        const deleteButton = event.target.closest('.delete-ingredient-btn');
        if (deleteButton) {
            const itemId = deleteButton.dataset.id;
            const url = deleteButton.dataset.url;

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
                    document.querySelectorAll(`[data-ingredient-id="${itemId}"]`).forEach(function (element) {
                        element.remove();
                    });

                    updateInventoryCount();
                    showGlobalMessage('Ingredient deleted successfully.', 'success');
                } else {
                    showGlobalMessage(data.message || 'Delete failed.', 'danger');
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
                showGlobalMessage('Something went wrong while deleting the ingredient.', 'danger');
            });

            return;
        }

        const markCookedButton = event.target.closest('.mark-cooked-btn');
        if (markCookedButton) {
            const url = markCookedButton.dataset.url;
            const cookStatusMessage = document.getElementById('cook-status-message');

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
                    showGlobalMessage('Recipe marked as cooked successfully.', 'success');
                } else {
                    if (cookStatusMessage) {
                        cookStatusMessage.textContent = data.message || 'Action failed.';
                    }
                    showGlobalMessage(data.message || 'Failed to mark recipe as cooked.', 'danger');
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
                if (cookStatusMessage) {
                    cookStatusMessage.textContent = 'Something went wrong.';
                }
                showGlobalMessage('Something went wrong while updating the recipe.', 'danger');
            });
        }
    });
});