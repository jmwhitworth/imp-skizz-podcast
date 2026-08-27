document.addEventListener('DOMContentLoaded', () => {
    const htmx = window.htmx;

    const clearFilters = () => {
        const form = document.querySelector('#filters-form');
        if (!form) return;

        const seasonSelect = form.querySelector('#season');
        const searchInput = form.querySelector('#search');

        if (seasonSelect) {
            seasonSelect.value = 'all';
        }
        if (searchInput) {
            searchInput.value = '';
        }
        if (htmx) {
            htmx.trigger('#filters-form', 'submit');
            return;
        }
        form.requestSubmit();
    };

    const clearFiltersButton = document.querySelector('#clear-filters');
    if (clearFiltersButton) {
        clearFiltersButton.addEventListener('click', clearFilters);
    }

    setClearFiltersButtonVisibility();
});


const setClearFiltersButtonVisibility = () => {
    const clearFiltersButton = document.querySelector('#clear-filters');
    const isFiltered = document.querySelector('#season')?.value !== 'all' || document.querySelector('#search')?.value !== '';
    if (clearFiltersButton) {
        clearFiltersButton.style.display = isFiltered ? 'inline-block' : 'none';
    }
};


document.body.addEventListener('htmx:afterSwap', () => {
    setClearFiltersButtonVisibility();
});