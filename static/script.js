// API Base URL
const API_BASE = '/api';

// Global state
let authors = [];
let titles = [];
let currentAuthorId = null;
let currentTitleId = null;

// ==================== UTILITY FUNCTIONS ====================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showError(error) {
    console.error('Error:', error);
    showToast(error.message || 'An error occurred', 'error');
}

// Safe fetch helper: returns {ok, status, data, text}
async function safeFetchJson(url, opts) {
    const res = await fetch(url, opts);
    const text = await res.text();
    let data = null;
    try {
        data = text ? JSON.parse(text) : null;
    } catch (e) {
        // not JSON
    }
    return { ok: res.ok, status: res.status, data, text };
}

// ----------------- Locale helpers (Indian formats) -----------------
function formatCurrencyINR(value) {
    if (value === null || value === undefined || value === '') return '';
    const num = Number(value);
    if (isNaN(num)) return value;
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(num);
}

function formatDateDisplay(dateStr) {
    if (!dateStr) return '';
    // Accept YYYY-MM-DD (ISO) or already DD-MM-YYYY
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        const [y, m, d] = dateStr.split('-');
        return `${d}-${m}-${y}`;
    }
    if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) return dateStr;
    return dateStr;
}

function dateForInput(value) {
    // Return YYYY-MM-DD for input[type=date]
    if (!value) return '';
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value;
    if (/^\d{2}-\d{2}-\d{4}$/.test(value)) {
        const [d, m, y] = value.split('-');
        return `${y}-${m}-${d}`;
    }
    return '';
}

// ==================== TAB NAVIGATION ====================

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
    });
});

// ==================== AUTHORS FUNCTIONALITY ====================

async function loadAuthors() {
    try {
        const response = await fetch(`${API_BASE}/authors`);
        const data = await response.json();
        
        if (data.success) {
            authors = data.data;
            renderAuthorsList();
            populateAuthorSelects();
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
}

function renderAuthorsList() {
    const container = document.getElementById('authorsList');
    
    if (authors.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-user-slash"></i>
                <p>No authors yet. Add your first author!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = authors.map(author => {
        const fullName = `${author.au_fname || ''} ${author.au_name}`.trim();
        const location = [author.city, author.state].filter(Boolean).join(', ');
        
        return `
            <div class="list-item" data-id="${author.au_id}">
                <div class="list-item-content">
                    <div class="list-item-title">${fullName}</div>
                    <div class="list-item-meta">
                        ${author.phone ? `<i class="fas fa-phone"></i> ${author.phone}` : ''}
                        ${location ? `<i class="fas fa-map-marker-alt"></i> ${location}` : ''}
                        ${author.contract ? '<i class="fas fa-file-contract"></i> Contract' : ''}
                    </div>
                </div>
                <div class="list-item-badge">${author.au_id}</div>
            </div>
        `;
    }).join('');
    
    // Add click handlers
    document.querySelectorAll('#authorsList .list-item').forEach(item => {
        item.addEventListener('click', () => selectAuthor(item.dataset.id));
    });
}

function selectAuthor(authorId) {
    currentAuthorId = authorId;
    const author = authors.find(a => a.au_id === authorId);
    
    if (!author) return;
    
    // Update form
    document.getElementById('authorId').value = author.au_id;
    document.getElementById('authorName').value = author.au_name;
    document.getElementById('authorFname').value = author.au_fname || '';
    document.getElementById('authorPhone').value = author.phone || '';
    document.getElementById('authorAddress').value = author.address || '';
    document.getElementById('authorCity').value = author.city || '';
    document.getElementById('authorState').value = author.state || '';
    document.getElementById('authorZip').value = author.zip || '';
    document.getElementById('authorContract').checked = author.contract || false;
    
    // Update buttons
    document.getElementById('addAuthorBtn').style.display = 'none';
    document.getElementById('updateAuthorBtn').style.display = 'inline-flex';
    document.getElementById('deleteAuthorBtn').style.display = 'inline-flex';
    document.getElementById('cancelAuthorBtn').style.display = 'inline-flex';
    
    // Highlight selected item
    document.querySelectorAll('#authorsList .list-item').forEach(item => {
        item.classList.toggle('active', item.dataset.id === authorId);
    });
}

function resetAuthorForm() {
    currentAuthorId = null;
    document.getElementById('authorForm').reset();
    document.getElementById('authorId').value = '';
    document.getElementById('addAuthorBtn').style.display = 'inline-flex';
    document.getElementById('updateAuthorBtn').style.display = 'none';
    document.getElementById('deleteAuthorBtn').style.display = 'none';
    document.getElementById('cancelAuthorBtn').style.display = 'none';
    
    document.querySelectorAll('#authorsList .list-item').forEach(item => {
        item.classList.remove('active');
    });
}

// Author Form Submit
document.getElementById('authorForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const authorData = {
        au_name: document.getElementById('authorName').value.trim(),
        au_fname: document.getElementById('authorFname').value.trim(),
        phone: document.getElementById('authorPhone').value.trim(),
        address: document.getElementById('authorAddress').value.trim(),
        city: document.getElementById('authorCity').value.trim(),
        state: document.getElementById('authorState').value.trim(),
        zip: document.getElementById('authorZip').value.trim(),
        contract: document.getElementById('authorContract').checked
    };
    
    try {
        const response = await fetch(`${API_BASE}/authors`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(authorData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Author added successfully!');
            resetAuthorForm();
            await loadAuthors();
            await loadTitles();
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
});

// Update Author
document.getElementById('updateAuthorBtn').addEventListener('click', async () => {
    if (!currentAuthorId) return;
    
    const authorData = {
        au_name: document.getElementById('authorName').value.trim(),
        au_fname: document.getElementById('authorFname').value.trim(),
        phone: document.getElementById('authorPhone').value.trim(),
        address: document.getElementById('authorAddress').value.trim(),
        city: document.getElementById('authorCity').value.trim(),
        state: document.getElementById('authorState').value.trim(),
        zip: document.getElementById('authorZip').value.trim(),
        contract: document.getElementById('authorContract').checked
    };
    
    try {
        const response = await fetch(`${API_BASE}/authors/${currentAuthorId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(authorData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Author updated successfully!');
            resetAuthorForm();
            await loadAuthors();
            await loadTitles();
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
});

// Delete Author
document.getElementById('deleteAuthorBtn').addEventListener('click', async () => {
    if (!currentAuthorId) return;
    
    if (!confirm('Are you sure you want to delete this author? All their titles will also be deleted.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/authors/${currentAuthorId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message);
            resetAuthorForm();
            await loadAuthors();
            await loadTitles();
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
});

// Cancel Author Edit
document.getElementById('cancelAuthorBtn').addEventListener('click', resetAuthorForm);

// ==================== TITLES FUNCTIONALITY ====================

async function loadTitles() {
    try {
        const response = await fetch(`${API_BASE}/titles`);
        const data = await response.json();
        
        if (data.success) {
            titles = data.data;
            renderTitlesList();
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
}

function renderTitlesList() {
    const container = document.getElementById('titlesList');
    
    if (titles.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-book-open"></i>
                <p>No titles yet. Add your first title!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = titles.map(title => {
        // Format authors
        let authorsText = '';
        if (title.authors) {
            if (Array.isArray(title.authors)) {
                // If it's an array of author objects
                const authorNames = title.authors.map(author => 
                    `${author.au_fname || ''} ${author.au_name}`.trim()
                );
                if (authorNames.length > 2) {
                    authorsText = `${authorNames.slice(0, 2).join(', ')} +${authorNames.length - 2} more`;
                } else {
                    authorsText = authorNames.join(', ');
                }
            } else if (typeof title.authors === 'string') {
                // If it's already a string
                authorsText = title.authors;
            }
        }
        
        return `
        <div class="list-item" data-id="${title.title_id}">
            <div class="list-item-content">
                <div class="list-item-title">${title.title}</div>
                <div class="list-item-meta">
                    ${title.type ? `<i class="fas fa-tag"></i> ${title.type}` : ''}
                    ${title.price ? `<i class="fas fa-rupee-sign"></i> ${formatCurrencyINR(title.price)}` : ''}
                    ${authorsText ? `<i class="fas fa-user"></i> ${authorsText}` : ''}
                </div>
            </div>
            <div class="list-item-badge">${title.title_id}</div>
        </div>`;
    }).join('');
    
    // Add click handlers
    document.querySelectorAll('#titlesList .list-item').forEach(item => {
        item.addEventListener('click', () => selectTitle(item.dataset.id));
    });
}

async function selectTitle(titleId) {
    currentTitleId = titleId;
    
    try {
        const response = await fetch(`${API_BASE}/titles/${titleId}`);
        const data = await response.json();
        
        if (data.success) {
            const title = data.data;
            
            // Show edit form
            document.getElementById('editTitleSection').style.display = 'none';
            document.getElementById('editTitleForm').style.display = 'block';
            
            // Populate form
            document.getElementById('editTitleId').value = title.title_id;
            document.getElementById('editTitleName').value = title.title;
            document.getElementById('editTitleType').value = title.type || '';
            document.getElementById('editTitlePubId').value = title.pub_id || '';
            document.getElementById('editTitlePrice').value = title.price || '';
            document.getElementById('editTitleAdvance').value = title.advance || '';
            document.getElementById('editTitleRoyalty').value = title.royalty || '';
            document.getElementById('editTitleYtdSales').value = title.ytd_sales || '';
            document.getElementById('editTitlePubDate').value = dateForInput(title.pubdate) || '';
            document.getElementById('editTitleNotes').value = title.notes || '';
            
            // Populate author checkboxes with royalty inputs
            const authorsContainer = document.getElementById('editTitleAuthors');
            const linkedAuthors = {};
            title.authors.forEach(a => {
                linkedAuthors[a.au_id] = a.royaltyper || 100;
            });
            
            authorsContainer.innerHTML = authors.map(author => {
                const isLinked = linkedAuthors.hasOwnProperty(author.au_id);
                const royaltyPer = linkedAuthors[author.au_id] || 100;
                const fullName = `${author.au_fname || ''} ${author.au_name}`.trim();
                
                return `
                    <div class="author-royalty-item">
                        <input type="checkbox" 
                               id="edit-author-${author.au_id}" 
                               value="${author.au_id}"
                               ${isLinked ? 'checked' : ''}>
                        <label for="edit-author-${author.au_id}">${fullName}</label>
                        <input type="number" 
                               class="royalty-input" 
                               data-author="${author.au_id}"
                               min="0" 
                               max="100" 
                               value="${royaltyPer}"
                               placeholder="%" 
                               ${!isLinked ? 'disabled' : ''}>
                    </div>
                `;
            }).join('');
            
            // Add event listeners to enable/disable royalty inputs
            authorsContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                cb.addEventListener('change', (e) => {
                    const authorId = e.target.value;
                    const royaltyInput = authorsContainer.querySelector(`input[data-author="${authorId}"]`);
                    royaltyInput.disabled = !e.target.checked;
                    if (e.target.checked && !royaltyInput.value) {
                        royaltyInput.value = 100;
                    }
                });
            });
            
            // Highlight selected item
            document.querySelectorAll('#titlesList .list-item').forEach(item => {
                item.classList.toggle('active', item.dataset.id === titleId);
            });
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
}

function populateAuthorSelects() {
    const selects = [
        document.getElementById('titleAuthor'),
        document.getElementById('viewAuthorSelect')
    ];
    
    selects.forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select an author</option>' +
            authors.map(author => {
                const fullName = `${author.au_fname || ''} ${author.au_name}`.trim();
                return `<option value="${author.au_id}">${fullName} (${author.au_id})</option>`;
            }).join('');
        if (currentValue) select.value = currentValue;
    });
}

// Add Title Form Submit
document.getElementById('addTitleForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Prefer custom genre if provided
    const genreSelect = document.getElementById('titleType');
    const otherGenre = document.getElementById('titleGenreOther');
    const selectedGenre = (otherGenre && otherGenre.style.display !== 'none' && otherGenre.value.trim()) ? otherGenre.value.trim() : genreSelect.value.trim();

    // Get author information
    const authorId = document.getElementById('titleAuthor').value.trim();
    const royaltyPer = parseInt(document.getElementById('titleRoyaltyPer').value) || 100;
    
    // Validate that author is selected
    if (!authorId) {
        showToast('Please select an author', 'error');
        return;
    }
    
    const titleData = {
        title: document.getElementById('titleName').value.trim(),
        type: selectedGenre,
        pub_id: document.getElementById('titlePubId').value.trim(),
        price: document.getElementById('titlePrice').value.trim(),
        advance: document.getElementById('titleAdvance').value.trim(),
        royalty: document.getElementById('titleRoyalty').value.trim(),
        ytd_sales: document.getElementById('titleYtdSales').value.trim(),
        notes: document.getElementById('titleNotes').value.trim(),
        pubdate: document.getElementById('titlePubDate').value.trim(),
        authors: [{
            au_id: authorId,
            royaltyper: royaltyPer,
            au_ord: 1
        }]
    };
    
    try {
        const response = await fetch(`${API_BASE}/titles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(titleData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Title added successfully!');
            document.getElementById('addTitleForm').reset();
            await loadTitles();
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
});

// Edit Title Form Submit
document.getElementById('editTitleForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentTitleId) return;
    
    // Get selected authors with royalty percentages
    const authorsContainer = document.getElementById('editTitleAuthors');
    const selectedAuthors = [];
    
    authorsContainer.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
        const authorId = cb.value;
        const royaltyInput = authorsContainer.querySelector(`input[data-author="${authorId}"]`);
        selectedAuthors.push({
            au_id: authorId,
            royaltyper: parseInt(royaltyInput.value) || 100
        });
    });
    
    if (selectedAuthors.length === 0) {
        showToast('Please select at least one author', 'error');
        return;
    }
    
    // Prefer custom genre if provided for edit
    const editGenreSelect = document.getElementById('editTitleType');
    const editOtherGenre = document.getElementById('editTitleGenreOther');
    const editSelectedGenre = (editOtherGenre && editOtherGenre.style.display !== 'none' && editOtherGenre.value.trim()) ? editOtherGenre.value.trim() : editGenreSelect.value.trim();

    const titleData = {
        title: document.getElementById('editTitleName').value.trim(),
        type: editSelectedGenre,
        pub_id: document.getElementById('editTitlePubId').value.trim(),
        price: document.getElementById('editTitlePrice').value.trim(),
        advance: document.getElementById('editTitleAdvance').value.trim(),
        royalty: document.getElementById('editTitleRoyalty').value.trim(),
        ytd_sales: document.getElementById('editTitleYtdSales').value.trim(),
        notes: document.getElementById('editTitleNotes').value.trim(),
        pubdate: document.getElementById('editTitlePubDate').value.trim(),
        authors: selectedAuthors
    };
    
    try {
        const response = await fetch(`${API_BASE}/titles/${currentTitleId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(titleData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Title updated successfully!');
            await loadTitles();
            await selectTitle(currentTitleId); // Refresh the form
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
});

// Delete Title
document.getElementById('deleteTitleBtn').addEventListener('click', async () => {
    if (!currentTitleId) return;
    
    if (!confirm('Are you sure you want to delete this title?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/titles/${currentTitleId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Title deleted successfully!');
            currentTitleId = null;
            document.getElementById('editTitleSection').style.display = 'block';
            document.getElementById('editTitleForm').style.display = 'none';
            await loadTitles();
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
});

// ==================== VIEW BY AUTHOR ====================

document.getElementById('viewTitlesBtn').addEventListener('click', async () => {
    const authorId = document.getElementById('viewAuthorSelect').value;
    
    if (!authorId) {
        showToast('Please select an author', 'warning');
        return;
    }
    
    try {
        const [titlesResponse, authorResponse] = await Promise.all([
            fetch(`${API_BASE}/titles/by-author/${authorId}`),
            fetch(`${API_BASE}/authors/${authorId}`)
        ]);
        
        const titlesData = await titlesResponse.json();
        const authorData = await authorResponse.json();
        
        if (titlesData.success && authorData.success) {
            const author = authorData.data;
            const fullName = `${author.au_fname || ''} ${author.au_name}`.trim();
            
            // Update author information
            document.getElementById('selectedAuthorName').textContent = fullName;
            
            // Update contact information
            const phoneDisplay = document.getElementById('authorPhoneDisplay');
            phoneDisplay.textContent = author.phone || 'Not provided';
            phoneDisplay.closest('#authorContact').style.display = author.phone ? 'inline-flex' : 'none';
            
            // Update location
            const locationParts = [];
            if (author.city) locationParts.push(author.city);
            if (author.state) locationParts.push(author.state);
            if (author.zip) locationParts.push(author.zip);
            
            const locationText = document.getElementById('authorLocationText');
            locationText.textContent = locationParts.length > 0 ? locationParts.join(', ') : 'Location not specified';
            
            // Update stats
            document.getElementById('totalTitles').textContent = titlesData.data.length;
            
            // Calculate average royalty if there are titles
            if (titlesData.data.length > 0) {
                const totalRoyalty = titlesData.data.reduce((sum, title) => {
                    return sum + (parseFloat(title.royaltyper) || 0);
                }, 0);
                const avgRoyalty = (totalRoyalty / titlesData.data.length).toFixed(1);
                document.getElementById('authorRoyalty').textContent = avgRoyalty;
            } else {
                document.getElementById('authorRoyalty').textContent = '0';
            }
            
            // Update titles table
            const tbody = document.getElementById('titlesTableBody');
            
            if (titlesData.data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 40px;">
                            <i class="fas fa-book-open" style="font-size: 2rem; opacity: 0.3;"></i>
                            <p style="margin-top: 10px; color: var(--text-muted);">No titles found for this author</p>
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = titlesData.data.map(title => `
                    <tr>
                        <td>${title.title_id}</td>
                        <td>${title.title}</td>
                        <td>${title.type || '-'}</td>
                        <td>${title.price ? formatCurrencyINR(title.price) : '-'}</td>
                        <td>${title.royaltyper || '-'}%</td>
                        <td>${title.pubdate ? formatDateDisplay(title.pubdate) : '-'}</td>
                    </tr>
                `).join('');
            }
            
            // Show the results section with a smooth scroll
            const resultsSection = document.getElementById('viewTitlesResult');
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            showError(new Error(data.error));
        }
    } catch (error) {
        showError(error);
    }
});

// ==================== INITIALIZATION ====================

async function init() {
    try {
        await loadAuthors();
        await loadTitles();
        showToast('Application loaded successfully!');
    } catch (error) {
        showError(error);
    }
}

// Start the application
init();

// Genre select toggles for custom "Other" input
function setupGenreToggles() {
    const genreSelect = document.getElementById('titleType');
    const otherInput = document.getElementById('titleGenreOther');
    if (genreSelect && otherInput) {
        genreSelect.addEventListener('change', () => {
            otherInput.style.display = (genreSelect.value === 'other') ? 'block' : 'none';
        });
    }

    const editGenreSelect = document.getElementById('editTitleType');
    const editOtherInput = document.getElementById('editTitleGenreOther');
    if (editGenreSelect && editOtherInput) {
        editGenreSelect.addEventListener('change', () => {
            editOtherInput.style.display = (editGenreSelect.value === 'other') ? 'block' : 'none';
        });
    }
}

setupGenreToggles();
