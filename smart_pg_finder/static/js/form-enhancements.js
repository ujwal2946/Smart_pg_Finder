// Form Enhancements for Add PG & Fast Updates
document.addEventListener('DOMContentLoaded', function() {
    // Image Preview
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    if (imageUpload && imagePreview) {
        imageUpload.addEventListener('change', function(e) {
            imagePreview.innerHTML = '';
            const files = Array.from(e.target.files);
            if (files.length > 8) {
                alert('Maximum 8 images allowed');
                this.value = '';
                return;
            }
            files.forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const col = document.createElement('div');
                        col.className = 'col-3';
                        col.innerHTML = `
                            <div class="glass-card position-relative p-2 border-primary border-opacity-25" style="height: 100px;">
                                <img src="${e.target.result}" class="w-100 h-100 object-fit-cover rounded border" alt="Preview">
                                <button type="button" class="btn-close position-absolute top-0 end-0 m-1 bg-danger bg-opacity-75 rounded-circle p-1" onclick="this.parentElement.parentElement.remove()"></button>
                            </div>
                        `;
                        imagePreview.appendChild(col);
                    };
                    reader.readAsDataURL(file);
                }
            });
        });
    }

    // Submit Loader - FIXED: Re-enable after 5s timeout to prevent hanging
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            const btnText = this.querySelector('.btn-text');
            const btnLoader = this.querySelector('.btn-loader');
            btnText.classList.add('d-none');
            btnLoader.classList.remove('d-none');
            this.disabled = true;
            
            // Safety timeout - re-enable after 5 seconds regardless
            setTimeout(() => {
                btnText.classList.remove('d-none');
                btnLoader.classList.add('d-none');
                this.disabled = false;
            }, 5000);
        });
    }

    // Form Validation Styling
    const formControls = document.querySelectorAll('.form-control, .form-select, .form-check-input');
    formControls.forEach(control => {
        control.addEventListener('blur', function() {
            if (this.classList.contains('is-invalid')) {
                this.parentElement.classList.add('has-validation-error');
            } else if (this.checkValidity()) {
                this.parentElement.classList.add('has-validation-success');
            }
        });
    });

    // Global availability toggle support (for reusability)
    window.toggleAvailability = async function(pgId, badgeId, toggleBtn) {
        const badge = document.getElementById(badgeId);
        const icon = toggleBtn.querySelector('i');
        
        icon.classList.remove('fa-toggle-on', 'fa-toggle-off');
        icon.classList.add('fa-spinner', 'fa-spin');
        toggleBtn.disabled = true;
        
        try {
            const response = await fetch(`/pg/toggle-availability/${pgId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').getAttribute('content'),
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            
            if (data.success) {
                badge.textContent = data.status_text;
                badge.className = `badge ${data.badge_class} bg-opacity-90 px-3 py-2 fs-6 shadow`;
                icon.className = `fa-solid fa-toggle-${data.is_available ? 'off' : 'on'} fa-xs text-white`;
            } else {
                alert('Toggle failed: ' + (data.error || 'Unknown error'));
                icon.classList.add('fa-toggle-on'); 
            }
        } catch (error) {
            alert('Network error: ' + error.message);
        } finally {
            toggleBtn.disabled = false;
            icon.classList.remove('fa-spinner', 'fa-spin');
        }
    };

    // NEW: Fast PG Field Update (AJAX, instant UI feedback)
    window.updatePGField = async function(pgId, field, value, displayElementId = null) {
        const btnOrIcon = event ? event.target.closest('button, i') : null;
        if (btnOrIcon) {
            btnOrIcon.classList.add('fa-spinner', 'fa-spin');
            btnOrIcon.disabled = true;
        }

        // Optimistic UI update
        if (displayElementId) {
            const displayEl = document.getElementById(displayElementId);
            if (displayEl) displayEl.textContent = value;
        }

        try {
            const response = await fetch(`/pg/ajax-update/${pgId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').getAttribute('content'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ updates: { [field]: value } })
            });

            const data = await response.json();

            if (data.success) {
                // Success feedback (green flash)
                if (displayElementId) {
                    const el = document.getElementById(displayElementId);
                    if (el) {
                        el.style.transition = 'all 0.3s ease';
                        el.classList.add('border-success', 'border-opacity-50');
                        setTimeout(() => el.classList.remove('border-success', 'border-opacity-50'), 1000);
                    }
                }
            } else {
                alert('Update failed: ' + (data.error || 'Unknown error'));
                // Revert optimistic update
                location.reload(); // Quick revert for simplicity
            }
        } catch (error) {
            alert('Network error: ' + error.message);
            location.reload();
        } finally {
            if (btnOrIcon) {
                btnOrIcon.classList.remove('fa-spinner', 'fa-spin');
                btnOrIcon.disabled = false;
            }
        }
    };
});

