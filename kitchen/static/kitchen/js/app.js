/* ================================================================
   SmartKitchen — Application JavaScript
   
   This file handles all client-side interactivity:
   - AJAX ingredient CRUD (add, edit, delete without page reload)
   - AJAX "Mark as Cooked" for recipe detail
   - Client-side recipe search and filter
   - Client-side form validation for registration
   - Dynamic inventory count badge updates
   
   Design decisions:
   - Event delegation used for dynamically-added elements
   - All AJAX requests include CSRF token for Django security
   - Graceful degradation: forms still work without JS via POST
   ================================================================ */


/* ── Utility functions ── */

/**
 * Extract the CSRF token from Django's hidden input in the page.
 * Required for all POST requests to pass Django's CSRF protection.
 */
function getCSRFToken() {
    var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

/**
 * Display a temporary status message at the top of the page.
 * Uses Bootstrap alert classes and ARIA live region for accessibility.
 * @param {string} message - The message text to display
 * @param {string} type - Bootstrap alert type: 'success', 'danger', 'warning', 'info'
 */
function showGlobalMessage(message, type) {
    type = type || 'success';
    var container = document.getElementById('global-status-message');
    if (!container) return;

    container.innerHTML =
        '<div class="alert alert-' + type + ' alert-dismissible fade show rounded-4 shadow-sm mb-2" role="status">' +
            message +
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close notification"></button>' +
        '</div>';

    // Auto-dismiss after 5 seconds for non-error messages
    if (type !== 'danger') {
        setTimeout(function () {
            var alert = container.querySelector('.alert');
            if (alert) alert.remove();
        }, 5000);
    }
}

/**
 * Recalculate and update the "Total items: N" badge on the dashboard.
 * Counts unique data-ingredient-id attributes to avoid double-counting
 * (desktop table row + mobile card for the same item).
 */
function updateInventoryCount() {
    var elements = document.querySelectorAll('[data-ingredient-id]');
    var uniqueIds = new Set();
    elements.forEach(function (el) {
        uniqueIds.add(el.dataset.ingredientId);
    });

    var countBadge = document.getElementById('inventory-count-badge');
    if (countBadge) {
        countBadge.textContent = 'Total items: ' + uniqueIds.size;
    }

    // Show empty-state message when inventory is cleared
    var desktopBody = document.getElementById('inventory-table-body');
    var mobileList = document.getElementById('inventory-mobile-list');

    if (uniqueIds.size === 0) {
        if (desktopBody) {
            desktopBody.innerHTML =
                '<tr><td colspan="5" class="text-center text-muted py-4">' +
                'No ingredients in your inventory yet. Add one to get started!</td></tr>';
        }
        if (mobileList) {
            mobileList.innerHTML =
                '<div class="text-center text-muted py-4">' +
                'No ingredients in your inventory yet. Add one to get started!</div>';
        }
    }
}

/**
 * Determine the expiry status of an ingredient based on its date.
 * Returns an object with CSS class and human-readable label.
 * @param {string} dateStr - Date string in YYYY-MM-DD format
 * @returns {{ statusClass: string, statusLabel: string }}
 */
function getExpiryStatus(dateStr) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    var expiry = new Date(dateStr + 'T00:00:00');
    var diffDays = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
        return { statusClass: 'danger', statusLabel: 'Expired' };
    } else if (diffDays <= 3) {
        return { statusClass: 'warning', statusLabel: 'Expiring Soon' };
    } else {
        return { statusClass: 'success', statusLabel: 'Fresh' };
    }
}


/* ── Main initialisation ── */

document.addEventListener('DOMContentLoaded', function () {
    updateInventoryCount();
    initDeleteIngredient();
    initAddIngredient();
    initEditIngredient();
    initMarkCooked();
    initRecipeSearch();
    initRecipeFilters();
    initRecipeChips();
    initFormValidation();
});


/* ── AJAX: Delete ingredient ── */

/**
 * Handle ingredient deletion via AJAX POST.
 * Uses event delegation so dynamically-added delete buttons also work.
 * On success, removes both the desktop table row and mobile card
 * for the deleted item (they share the same data-ingredient-id).
 */
function initDeleteIngredient() {
    document.addEventListener('click', function (event) {
        var btn = event.target.closest('.delete-ingredient-btn');
        if (!btn) return;

        event.preventDefault();

        var itemId = btn.dataset.id;
        var itemName = btn.dataset.name || 'this ingredient';

        // Enter your name and ID in the HTML form
        document.getElementById('delete-item-id').value = itemId;
        document.getElementById('delete-item-name').innerText = itemName;

        // Pop-up window (Modal)
        var deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        deleteModal.show();
    });

    // When the user clicks the red “Delete” confirmation button in the pop-up window
    var confirmBtn = document.getElementById('confirm-delete-btn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function () {
            var itemId = document.getElementById('delete-item-id').value;
            // Get the current picture-in-picture instance so that it can be closed later
            var modalElement = document.getElementById('deleteConfirmModal');
            var modalInstance = bootstrap.Modal.getInstance(modalElement);


        fetch('/ingredients/delete/' + itemId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 1. close the window
                    modalInstance.hide();

                    // 2. delet this line
                    document.querySelectorAll('[data-ingredient-id="' + itemId + '"]').forEach(function (el) {
                        el.remove();
                    });

                    // 3. Update the “Total Items” count in the upper-left corner
                    if (typeof updateInventoryCount === 'function') updateInventoryCount();

                    // 4. success message appears
                    showGlobalMessage(data.message || 'Deleted successfully!');
                } else {
                    showGlobalMessage(data.message || 'Delete failed.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showGlobalMessage('Network error, please try again.', 'danger');
            });
        });
    }
}


/* ── AJAX: Add ingredient ── */

/**
 * Handle the "Add Ingredient" form submission via AJAX.
 * Performs client-side validation first, then sends data to the server.
 * On success, dynamically inserts a new row into both the desktop table
 * and the mobile card list (no page reload required).
 */
function initAddIngredient() {
    var form = document.getElementById('add-ingredient-form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        // Gather form values
        var nameInput = document.getElementById('ingredient-name');
        var qtyInput = document.getElementById('ingredient-quantity');
        var unitSelect = document.getElementById('ingredient-unit');
        var expiryInput = document.getElementById('ingredient-expiry');

        // Reset previous validation states
        [nameInput, qtyInput, expiryInput].forEach(function (input) {
            input.classList.remove('is-invalid');
        });

        const addError = document.getElementById('add-error-msg');
        if (addError) addError.classList.add('d-none');

        // Client-side validation: check required fields before server call
        var isValid = true;

        if (!nameInput.value.trim()) {
            nameInput.classList.add('is-invalid');
            isValid = false;
        }
        if (!qtyInput.value || parseFloat(qtyInput.value) <= 0) {
            qtyInput.classList.add('is-invalid');
            isValid = false;
        }
        if (!expiryInput.value) {
            expiryInput.classList.add('is-invalid');
            isValid = false;
        }

        if (!isValid) {
            const errorDiv = document.getElementById('add-error-msg'); 
            errorDiv.innerText = 'Please fill in all required fields correctly.';
            errorDiv.classList.remove('d-none');
            return;
        }

        var payload = {
            name: nameInput.value.trim(),
            quantity: parseFloat(qtyInput.value),
            unit: unitSelect.value,
            expiry_date: expiryInput.value
        };

        fetch('/ingredients/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                // Generate a temporary client-side ID for the new row
                document.getElementById('add-error-msg').classList.add('d-none');
                document.getElementById('add-ingredient-form').reset();
                var newId = data.id || ('temp-' + Date.now());
                var status = getExpiryStatus(payload.expiry_date);

                // Insert into desktop table
                insertDesktopRow(newId, payload, status);
                // Insert into mobile card list
                insertMobileCard(newId, payload, status);

                // Clear the form inputs
                updateInventoryCount();
                showGlobalMessage(payload.name + ' added to inventory!');
            } else {
                showGlobalMessage(data.message || 'Failed to add ingredient.', 'danger');
            }
        })
        .catch(function () {
            showGlobalMessage('Network error. Please try again.', 'danger');
        });
    });
}

/**
 * Insert a new row into the desktop inventory table.
 * Removes any "no items" placeholder row first.
 */
function insertDesktopRow(id, item, status) {
    var tbody = document.getElementById('inventory-table-body');
    if (!tbody) return;

    // Remove empty-state placeholder if present
    var emptyRow = tbody.querySelector('td[colspan]');
    if (emptyRow) emptyRow.closest('tr').remove();

    var tr = document.createElement('tr');
    tr.setAttribute('data-ingredient-id', id);
    const dateObj = new Date(item.expiry_date);
    const formattedDate = dateObj.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });

    tr.innerHTML =
        '<td>' + escapeHtml(item.name) + '</td>' +
        '<td>' + item.quantity + ' ' + escapeHtml(item.unit) + '</td>' +
        '<td>' + item.expiry_date + '</td>' +
        '<td><span class="badge badge-soft-' + status.statusClass + '">' + status.statusLabel + '</span></td>' +
        '<td class="text-end">' +
            '<button type="button" class="btn btn-outline-secondary btn-sm edit-ingredient-btn"' +
                ' data-id="' + id + '"' +
                ' data-name="' + escapeHtml(item.name) + '"' +
                ' data-quantity="' + item.quantity + '"' +
                ' data-unit="' + escapeHtml(item.unit) + '"' +
                ' data-expiry="' + item.expiry_date + '"' +
                ' aria-label="Edit ' + escapeHtml(item.name) + '">' +
                '<i class="bi bi-pencil" aria-hidden="true"></i> Edit</button> ' +
            '<button type="button" class="btn btn-outline-danger btn-sm delete-ingredient-btn"' +
                ' data-id="' + id + '" data-name="' + escapeHtml(item.name) + '"' +
                ' aria-label="Delete ' + escapeHtml(item.name) + '">' +
                '<i class="bi bi-trash" aria-hidden="true"></i> Delete</button>' +
        '</td>';
    tbody.appendChild(tr);
}

/**
 * Insert a new mobile card into the mobile inventory list.
 */
function insertMobileCard(id, item, status) {
    var mobileList = document.getElementById('inventory-mobile-list');
    if (!mobileList) return;

    // Remove empty-state placeholder if present
    var emptyDiv = mobileList.querySelector('.text-center.text-muted');
    if (emptyDiv) emptyDiv.remove();

    var card = document.createElement('div');
    card.className = 'card p-3 mb-3 inventory-mobile-card';
    card.setAttribute('data-ingredient-id', id);
    card.innerHTML =
        '<div class="d-flex justify-content-between align-items-start gap-2 mb-2">' +
            '<div><div class="fw-bold">' + escapeHtml(item.name) + '</div>' +
            '<div class="text-muted small">' + item.quantity + ' ' + escapeHtml(item.unit) + '</div></div>' +
            '<span class="badge badge-soft-' + status.statusClass + '">' + status.statusLabel + '</span>' +
        '</div>' +
        '<div class="small text-muted mb-3">Expiry: ' + item.expiry_date + '</div>' +
        '<div class="d-flex gap-2">' +
            '<button type="button" class="btn btn-outline-secondary btn-sm flex-fill edit-ingredient-btn"' +
                ' data-id="' + id + '" data-name="' + escapeHtml(item.name) + '"' +
                ' data-quantity="' + item.quantity + '" data-unit="' + escapeHtml(item.unit) + '"' +
                ' data-expiry="' + item.expiry_date + '">Edit</button>' +
            '<button type="button" class="btn btn-outline-danger btn-sm flex-fill delete-ingredient-btn"' +
                ' data-id="' + id + '" data-name="' + escapeHtml(item.name) + '">Delete</button>' +
        '</div>';
    mobileList.appendChild(card);
}

/** Escape HTML to prevent XSS when inserting user-provided text into the DOM. */
function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


/* ── AJAX: Edit ingredient ── */

/**
 * Open the edit modal pre-filled with ingredient data,
 * then save changes via AJAX on confirmation.
 * Uses Bootstrap modal API and event delegation.
 */
function initEditIngredient() {
    var modal = document.getElementById('editIngredientModal');
    if (!modal) return;

    var bsModal = new bootstrap.Modal(modal);

    // Open modal and populate fields when Edit button is clicked
    document.addEventListener('click', function (event) {
        var btn = event.target.closest('.edit-ingredient-btn');
        if (!btn) return;

        document.getElementById('edit-id').value = btn.dataset.id;
        document.getElementById('edit-name').value = btn.dataset.name;
        document.getElementById('edit-quantity').value = btn.dataset.quantity;
        document.getElementById('edit-unit').value = btn.dataset.unit;
        document.getElementById('edit-expiry').value = btn.dataset.expiry;

        bsModal.show();
    });

    // Save changes via AJAX when "Save Changes" is clicked
    var saveBtn = document.getElementById('save-edit-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            document.getElementById('edit-error-msg').classList.add('d-none');
            var itemId = document.getElementById('edit-id').value;
            var payload = {
                name: document.getElementById('edit-name').value.trim(),
                quantity: parseFloat(document.getElementById('edit-quantity').value),
                unit: document.getElementById('edit-unit').value,
                expiry_date: document.getElementById('edit-expiry').value
            };

            if (!payload.name || !payload.quantity || !payload.expiry_date) {
                const errorDiv = document.getElementById('edit-error-msg');
                if (errorDiv) {
                    errorDiv.innerText = 'Please fill in all fields.';
                    errorDiv.classList.remove('d-none'); 
                }
                return;
            }

            fetch('/ingredients/edit/' + itemId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(payload)
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.success) {
                    // Update the DOM in-place for both desktop and mobile views
                    var status = getExpiryStatus(payload.expiry_date);
                    updateIngredientInDOM(itemId, payload, status);
                    bsModal.hide();
                    showGlobalMessage(payload.name + ' updated successfully.');
                } else {
                    showGlobalMessage(data.message || 'Update failed.', 'danger');
                }
            })
            .catch(function () {
                showGlobalMessage('Network error. Please try again.', 'danger');
            });
        });
    }
}

/**
 * Update the ingredient display in both desktop table and mobile card
 * after a successful edit. Avoids full page reload.
 */
function updateIngredientInDOM(id, item, status) {
    // Update desktop table row
    var row = document.querySelector('tr[data-ingredient-id="' + id + '"]');
    if (row) {
        var cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            cells[0].textContent = item.name;
            cells[1].textContent = item.quantity + ' ' + item.unit;
            cells[2].textContent = item.expiry_date;
            cells[3].innerHTML = '<span class="badge badge-soft-' + status.statusClass + '">' + status.statusLabel + '</span>';
        }
        // Update data attributes on edit/delete buttons
        row.querySelectorAll('.edit-ingredient-btn, .delete-ingredient-btn').forEach(function (btn) {
            btn.dataset.name = item.name;
            if (btn.classList.contains('edit-ingredient-btn')) {
                btn.dataset.quantity = item.quantity;
                btn.dataset.unit = item.unit;
                btn.dataset.expiry = item.expiry_date;
            }
        });
    }

    // Update mobile card
    var card = document.querySelector('.inventory-mobile-card[data-ingredient-id="' + id + '"]');
    if (card) {
        var nameEl = card.querySelector('.fw-bold');
        var qtyEl = card.querySelector('.text-muted.small');
        var expiryEl = card.querySelectorAll('.small.text-muted')[1] || card.querySelector('.small.text-muted.mb-3');
        var badge = card.querySelector('.badge');

        if (nameEl) nameEl.textContent = item.name;
        if (qtyEl) qtyEl.textContent = item.quantity + ' ' + item.unit;
        if (expiryEl) expiryEl.textContent = 'Expiry: ' + item.expiry_date;
        if (badge) {
            badge.className = 'badge badge-soft-' + status.statusClass;
            badge.textContent = status.statusLabel;
        }
    }
}


/* ── AJAX: Mark recipe as cooked ── */

/**
 * Send AJAX POST to mark a recipe as cooked.
 * Updates the button state and shows confirmation feedback.
 */
function initMarkCooked() {
    document.addEventListener('click', function (event) {
        var btn = event.target.closest('.mark-cooked-btn');
        if (!btn) return;

        var url = btn.dataset.url;
        var statusMsg = document.getElementById('cook-status-message');

        // Disable button to prevent double-clicks
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split me-1" aria-hidden="true"></i>Updating...';

        var recipeId = btn.dataset.recipeId;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                'recipe_id': recipeId 
            })
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                btn.innerHTML = '<i class="bi bi-check-circle-fill me-1" aria-hidden="true"></i>Cooked!';
                btn.classList.remove('btn-success');
                btn.classList.add('btn-outline-success');
                if (statusMsg) statusMsg.textContent = data.message || 'Inventory updated.';
                showGlobalMessage('Recipe marked as cooked! Inventory updated.');
            } else {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-check2-circle me-1" aria-hidden="true"></i>Mark as Cooked';
                if (statusMsg) statusMsg.textContent = data.message || 'Action failed.';
                showGlobalMessage(data.message || 'Failed to mark recipe as cooked.', 'danger');
            }
        })
        .catch(function () {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check2-circle me-1" aria-hidden="true"></i>Mark as Cooked';
            showGlobalMessage('Network error. Please try again.', 'danger');
        });
    });
}


/* ── Client-side recipe search ── */

/**
 * Filter recipe cards in real time as the user types in the search box.
 * Matches against the recipe name stored in data-name attribute.
 * Updates the visible result count dynamically.
 */
function initRecipeSearch() {
    var searchInput = document.getElementById('recipe-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', function () {
        applyRecipeFilters();
    });
}


/* ── Client-side recipe dropdown filters ── */

/**
 * Attach change listeners to the cooking time, difficulty, and
 * dietary filter dropdowns. All filtering is done client-side
 * by reading data attributes on recipe card wrappers.
 */
function initRecipeFilters() {
    var filterIds = ['filter-cook-time', 'filter-difficulty', 'filter-dietary'];
    filterIds.forEach(function (id) {
        var el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', function () {
                applyRecipeFilters();
            });
        }
    });
}


/* ── Client-side recipe chip (quick-filter tag) toggle ── */

/**
 * Chips act as toggleable quick-filter buttons.
 * Clicking a chip toggles its "active" state and re-applies filters.
 * Chip tags map to data-tags attribute on recipe cards.
 */
function initRecipeChips() {
    document.querySelectorAll('.recipe-chip').forEach(function (chip) {
        chip.addEventListener('click', function () {
            chip.classList.toggle('active');
            applyRecipeFilters();
        });
    });
}


/**
 * Core filtering logic: combines search text, dropdown selections,
 * and active chip tags to show/hide recipe cards.
 * Called whenever any filter input changes.
 */
function applyRecipeFilters() {
    var searchInput = document.getElementById('recipe-search');
    var cookTimeSelect = document.getElementById('filter-cook-time');
    var difficultySelect = document.getElementById('filter-difficulty');
    var dietarySelect = document.getElementById('filter-dietary');
    var grid = document.getElementById('recipe-grid');
    if (!grid) return;

    var query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    var cookTimeVal = cookTimeSelect ? cookTimeSelect.value : 'any';
    var difficultyVal = difficultySelect ? difficultySelect.value.toLowerCase() : 'any';
    var dietaryVal = dietarySelect ? dietarySelect.value.toLowerCase() : 'any';

    // Collect active chip tags
    var activeTags = [];
    document.querySelectorAll('.recipe-chip.active').forEach(function (chip) {
        activeTags.push(chip.dataset.filterTag);
    });

    var cards = grid.querySelectorAll('.recipe-card-wrapper');
    var visibleCount = 0;

    cards.forEach(function (card) {
        var name = card.dataset.name || '';
        var cookTime = parseInt(card.dataset.cookTime, 10) || 0;
        var difficulty = (card.dataset.difficulty || '').toLowerCase();
        var dietary = (card.dataset.dietary || '').toLowerCase();
        var tags = (card.dataset.tags || '').toLowerCase();
        var show = true;

        // Search filter: match against recipe name
        if (query && name.indexOf(query) === -1) {
            show = false;
        }

        // Cooking time filter
        if (show && cookTimeVal !== 'any') {
            var maxTime = parseInt(cookTimeVal, 10);
            if (maxTime <= 30 && cookTime > maxTime) show = false;
            if (maxTime > 30 && cookTime < 30) show = false;
        }

        // Difficulty filter
        if (show && difficultyVal !== 'any' && difficulty !== difficultyVal) {
            show = false;
        }

        // Dietary filter
        if (show && dietaryVal !== 'any' && dietary.indexOf(dietaryVal) === -1) {
            show = false;
        }

        // Chip tag filter: card must match ALL active tags
        if (show && activeTags.length > 0) {
            for (var i = 0; i < activeTags.length; i++) {
                if (tags.indexOf(activeTags[i]) === -1) {
                    show = false;
                    break;
                }
            }
        }

        card.style.display = show ? '' : 'none';
        if (show) visibleCount++;
    });

    // Update result count text
    var countEl = document.getElementById('recipe-result-count');
    if (countEl) {
        countEl.textContent = visibleCount + ' result' + (visibleCount !== 1 ? 's' : '');
    }

    // Show/hide "no results" message
    var noResults = document.getElementById('no-filter-results');
    if (noResults) {
        noResults.classList.toggle('d-none', visibleCount > 0);
    }
}


/* ── Client-side form validation (registration page) ── */

/**
 * Add real-time validation feedback to the registration form.
 * Validates email format and password match before submission.
 * This is in addition to server-side Django validation.
 */
function initFormValidation() {
    var registerForm = document.getElementById('register-form');
    if (!registerForm) return;

    registerForm.addEventListener('submit', function (event) {
        var email = document.getElementById('id_email');
        var pw1 = document.getElementById('id_password1');
        var pw2 = document.getElementById('id_password2');
        var isValid = true;

        // Validate email format
        if (email && email.value && !email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            email.classList.add('is-invalid');
            isValid = false;
        } else if (email) {
            email.classList.remove('is-invalid');
        }

        // Validate password match
        if (pw1 && pw2 && pw1.value !== pw2.value) {
            pw2.classList.add('is-invalid');
            // Add dynamic error message if not already present
            var feedback = pw2.parentElement.querySelector('.invalid-feedback');
            if (!feedback) {
                var div = document.createElement('div');
                div.className = 'invalid-feedback d-block';
                div.setAttribute('role', 'alert');
                div.textContent = 'Passwords do not match.';
                pw2.parentElement.appendChild(div);
            }
            isValid = false;
        } else if (pw2) {
            pw2.classList.remove('is-invalid');
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
}
