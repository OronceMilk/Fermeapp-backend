// filters.js - Gestion des filtres HTMX

let filterTimeout = null;

// Synchronisation des filtres avec l'URL
function syncFiltersWithURL() {
    const url = new URL(window.location);
    const params = url.searchParams;

    // Récupérer les valeurs des filtres depuis l'URL
    document.querySelectorAll('[name]').forEach(element => {
        const name = element.name;
        const value = params.get(name);
        if (value !== null) {
            if (element.type === 'checkbox') {
                element.checked = value === 'on';
            } else {
                element.value = value;
            }
        }
    });

    // Mettre à jour le compteur de filtres actifs
    updateActiveFiltersCount();
}

// Mise à jour du compteur de filtres actifs
function updateActiveFiltersCount() {
    const activeFilters = Array.from(document.querySelectorAll('[name]'))
        .filter(element => {
            if (element.type === 'checkbox') {
                return element.checked;
            } else {
                return element.value && element.value.trim() !== '';
            }
        })
        .length;

    const counter = document.getElementById('filter-count');
    if (counter) {
        counter.textContent = activeFilters;
    }

    // Mettre en évidence les filtres actifs
    highlightActiveFilters();
}

// Mise en évidence des filtres actifs
function highlightActiveFilters() {
    document.querySelectorAll('[name]').forEach(element => {
        const isActive = element.type === 'checkbox' ?
            element.checked :
            element.value && element.value.trim() !== '';

        const container = element.closest('.filter-container') || element.parentElement;
        if (container) {
            if (isActive) {
                container.classList.add('ring-2', 'ring-blue-500', 'ring-opacity-50');
            } else {
                container.classList.remove('ring-2', 'ring-blue-500', 'ring-opacity-50');
            }
        }
    });
}

// Fonction de debounce pour les recherches
function debounceFilters(callback, delay = 300) {
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(callback, delay);
}

// Gestionnaire d'événement pour les changements de filtres
function handleFilterChange(event) {
    const element = event.target;

    // Mettre à jour l'URL
    updateURLWithFilters();

    // Mettre à jour le compteur
    updateActiveFiltersCount();

    // Pour les inputs de recherche, utiliser debounce
    if (element.type === 'text' && element.hasAttribute('hx-trigger')) {
        const trigger = element.getAttribute('hx-trigger');
        if (trigger.includes('delay')) {
            debounceFilters(() => {
                // La requête HTMX sera déclenchée automatiquement
            });
        }
    }
}

// Mise à jour de l'URL avec les filtres actuels
function updateURLWithFilters() {
    const url = new URL(window.location);
    const params = url.searchParams;

    // Nettoyer les paramètres existants
    Array.from(params.keys()).forEach(key => {
        if (key !== 'page') { // Garder le paramètre de pagination
            params.delete(key);
        }
    });

    // Ajouter les valeurs actuelles des filtres
    document.querySelectorAll('[name]').forEach(element => {
        const name = element.name;
        let value = null;

        if (element.type === 'checkbox') {
            value = element.checked ? 'on' : null;
        } else {
            value = element.value && element.value.trim() !== '' ? element.value : null;
        }

        if (value !== null) {
            params.set(name, value);
        }
    });

    // Mettre à jour l'URL sans recharger la page
    window.history.replaceState({}, '', url.toString());
}

// Fonction pour effacer tous les filtres
function clearFilters() {
    document.querySelectorAll('[name]').forEach(element => {
        if (element.type === 'checkbox') {
            element.checked = false;
        } else {
            element.value = '';
        }
    });

    // Mettre à jour l'URL et les compteurs
    updateURLWithFilters();
    updateActiveFiltersCount();

    // Déclencher une requête HTMX pour actualiser les résultats
    const firstFilter = document.querySelector('[name]');
    if (firstFilter && firstFilter.hasAttribute('hx-get')) {
        htmx.trigger(firstFilter, 'change');
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Synchroniser les filtres avec l'URL au chargement
    syncFiltersWithURL();

    // Ajouter les gestionnaires d'événements
    document.querySelectorAll('[name]').forEach(element => {
        element.addEventListener('change', handleFilterChange);
        element.addEventListener('input', handleFilterChange);
    });

    // Gestion spéciale pour les inputs de recherche avec debounce
    document.querySelectorAll('input[type="text"][name]').forEach(input => {
        input.addEventListener('input', function() {
            debounceFilters(() => {
                handleFilterChange({ target: input });
            });
        });
    });
});

// Gestionnaire HTMX pour mettre à jour les filtres après les requêtes
document.addEventListener('htmx:afterRequest', function(event) {
    // Après une requête HTMX, mettre à jour les compteurs
    setTimeout(updateActiveFiltersCount, 100);
});

// Export des fonctions pour utilisation globale
window.syncFiltersWithURL = syncFiltersWithURL;
window.updateActiveFiltersCount = updateActiveFiltersCount;
window.highlightActiveFilters = highlightActiveFilters;
window.clearFilters = clearFilters;