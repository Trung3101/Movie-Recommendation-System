/**
 * CineMate - Frontend JavaScript
 * Handles all AJAX interactions and UI updates
 */

// Global variables
let currentMovieId = null;
let currentRating = 0;
let filterData = null; // NEW: Store filter data

// Base URL for TMDB posters
const POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500";

/**
 * Document Ready
 */
$(document).ready(function() {
    console.log("✅ CineMate initialized");
    
    // Bind event handlers
    bindEventHandlers();
    
    // Load filter data for Flexible Search mode
    loadFilterData();
});

/**
 * Bind all event handlers
 */
function bindEventHandlers() {
    // Manual Search mode
    $('#searchForm').on('submit', handleSearch);
    
    // Rating button clicks
    $('.rating-btn').on('click', handleRatingClick);
    
    // Rate movie button
    $('#rateMovieBtn').on('click', handleRateMovie);
    
    // Flexible Search mode
    bindFilterEventHandlers();
}

/**
 * Bind filter-related event handlers
 */
function bindFilterEventHandlers() {
    // Collapsible filter sections
    $('.filter-section-header').on('click', handleFilterSectionToggle);
    
    // Filter tag clicks (delegated for dynamic content)
    $(document).on('click', '.filter-tag', handleFilterTagClick);
    
    // Apply filters button
    $('#applyFiltersBtn').on('click', handleApplyFilters);
    
    // Clear filters button
    $('#clearFiltersBtn').on('click', handleClearFilters);
}

/**
 * Handle search form submission
 */
function handleSearch(e) {
    e.preventDefault();
    
    const movieName = $('#movieNameInput').val().trim();
    
    if (!movieName) {
        alert('Vui lòng nhập tên phim!');
        return;
    }
    
    console.log(`🔍 Searching for: ${movieName}`);
    
    // Show loading spinner
    $('#loadingSpinner').show();
    $('#resultsContainer').hide();
    
    // Make AJAX request
    $.ajax({
        url: '/search',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            movie_name: movieName
        }),
        success: function(response) {
            console.log('✅ Search successful:', response);
            
            // Hide loading
            $('#loadingSpinner').hide();
            
            // Display results
            displayResults(response);
            
            // Show results container
            $('#resultsContainer').show();
            
            // Smooth scroll to results
            $('html, body').animate({
                scrollTop: $('#resultsContainer').offset().top - 100
            }, 500);
        },
        error: function(xhr, status, error) {
            console.error('❌ Search failed:', error);
            
            $('#loadingSpinner').hide();
            
            const errorMsg = xhr.responseJSON?.error || 'Lỗi khi tìm kiếm phim. Vui lòng thử lại!';
            alert(errorMsg);
        }
    });
}

/**
 * Display search results in carousels
 */
function displayResults(data) {
    // Display related movies
    displayMovieCarousel('related', data.related, '#relatedMoviesContainer', '#relatedMoviesEmpty');
    
    // Display similar movies
    displayMovieCarousel('similar', data.similar, '#similarMoviesContainer', '#similarMoviesEmpty');
    
    // Display personalized movies
    displayMovieCarousel('personalized', data.personalized, '#personalizedMoviesContainer', '#personalizedMoviesEmpty');
}

/**
 * Display movies in a carousel
 */
function displayMovieCarousel(type, movies, containerSelector, emptySelector) {
    const $container = $(containerSelector);
    const $empty = $(emptySelector);
    
    // Clear previous content
    $container.empty();
    
    // Check if movies list is empty
    if (!movies || movies.length === 0) {
        $container.parent().hide();
        $empty.show();
        return;
    }
    
    // Hide empty message
    $empty.hide();
    $container.parent().show();
    
    // Split movies into groups of 4 for carousel items
    const chunkSize = 4;
    const movieChunks = [];
    
    for (let i = 0; i < movies.length; i += chunkSize) {
        movieChunks.push(movies.slice(i, i + chunkSize));
    }
    
    // Create carousel items
    movieChunks.forEach((chunk, index) => {
        const isActive = index === 0 ? 'active' : '';
        
        let carouselItem = `
            <div class="carousel-item ${isActive}">
                <div class="row">
        `;
        
        chunk.forEach(movie => {
            carouselItem += createMovieCard(movie);
        });
        
        carouselItem += `
                </div>
            </div>
        `;
        
        $container.append(carouselItem);
    });
    
    console.log(`✅ Displayed ${movies.length} ${type} movies`);
}

/**
 * Create a movie card HTML
 */
function createMovieCard(movie) {
    const posterUrl = movie.poster_path 
        ? `${POSTER_BASE_URL}${movie.poster_path}`
        : 'https://via.placeholder.com/300x450?text=No+Poster';
    
    const movieName = movie.movie_name || 'N/A';
    const genres = movie.genres || 'N/A';
    const director = movie.director || 'N/A';
    const year = movie.release_year || 'N/A';
    const overview = movie.overview || 'N/A';
    
    // 🔧 FIX: Ưu tiên lấy 'id', sau đó 'movieId'
    const movieId = movie.id || movie.movieId || 0;
    
    console.log(`📌 DEBUG createMovieCard: movie.id=${movie.id}, movie.movieId=${movie.movieId}, final movieId=${movieId}`);
    
    // Parse genres and create badges (replace | with ,)
    let genreBadges = '';
    if (genres && genres !== 'N/A') {
        const genreList = genres.split('|').slice(0, 3); // Limit to 3 genres
        genreList.forEach(genre => {
            genreBadges += `<span class="genre-badge">${genre.trim()}</span>`;
        });
    }
    
    return `
        <div class="col-md-3 mb-3">
            <div class="movie-card" 
                 data-movie-id="${movieId}"
                 data-movie-name="${escapeHtml(movieName)}"
                 data-genres="${escapeHtml(genres)}"
                 data-director="${escapeHtml(director)}"
                 data-year="${year}"
                 data-poster="${escapeHtml(posterUrl)}"
                 data-overview="${escapeHtml(overview)}"
                 onclick="showMovieDetail(this)">
                <img src="${posterUrl}" 
                     alt="${escapeHtml(movieName)}" 
                     class="movie-card-img"
                     onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
                <div class="movie-card-body">
                    <h5 class="movie-card-title">${escapeHtml(movieName)}</h5>
                    <p class="movie-card-info">
                        <i class="bi bi-calendar3"></i> ${year}
                    </p>
                    <p class="movie-card-info">
                        <i class="bi bi-person-video2"></i> ${escapeHtml(director)}
                    </p>
                    <div class="movie-card-genres">
                        ${genreBadges}
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Show movie detail modal
 */
function showMovieDetail(element) {
    const $card = $(element);
    
    // Get movie data from card attributes
    currentMovieId = $card.data('movie-id');
    const movieName = $card.data('movie-name');
    const genres = $card.data('genres');
    const director = $card.data('director');
    const year = $card.data('year');
    const poster = $card.data('poster');
    const overview = $card.data('overview') || 'Không có thông tin';
    
    console.log(`📽️ DEBUG showMovieDetail: currentMovieId=${currentMovieId}, type=${typeof currentMovieId}`);
    
    // Kiểm tra nếu movieId không hợp lệ
    if (!currentMovieId || currentMovieId === 0 || currentMovieId === '0') {
        console.error('❌ Invalid movieId:', currentMovieId);
        alert('Lỗi: Không tìm thấy ID phim! Vui lòng thử lại.');
        return;
    }
    
    // Format genres: thay | bằng ,
    const formattedGenres = genres ? genres.replace(/\|/g, ', ') : 'N/A';
    
    // Truncate overview to 150 characters
    const truncatedOverview = overview && overview !== 'N/A' 
        ? (overview.length > 150 ? overview.substring(0, 150) + '...' : overview)
        : 'Không có thông tin';
    
    // Populate modal
    $('#modalMovieTitle').text(movieName);
    $('#modalMovieName').text(movieName);
    $('#modalMovieYear').text(year);
    $('#modalMovieGenres').text(formattedGenres);
    $('#modalMovieDirector').text(director);
    $('#modalMovieOverview').text(truncatedOverview);
    $('#modalMoviePoster').attr('src', poster);
    
    // Reset rating
    currentRating = 0;
    $('.rating-btn').removeClass('active');
    
    // Show modal
    $('#movieDetailModal').modal('show');
    
    console.log(`📽️ Showing details for: ${movieName} (ID: ${currentMovieId})`);
}

/**
 * Handle rating button click
 */
function handleRatingClick(e) {
    const $btn = $(e.currentTarget);
    const rating = parseInt($btn.data('rating'));
    
    // Update current rating
    currentRating = rating;
    
    // Update button states
    $('.rating-btn').removeClass('active');
    $('.rating-btn').each(function() {
        if (parseInt($(this).data('rating')) <= rating) {
            $(this).addClass('active');
        }
    });
    
    console.log(`⭐ Selected rating: ${rating}`);
}

/**
 * Handle rate movie button click
 */
function handleRateMovie() {
    if (!currentMovieId) {
        alert('Lỗi: Không tìm thấy thông tin phim!');
        return;
    }
    
    if (currentRating === 0) {
        alert('Vui lòng chọn số sao đánh giá!');
        return;
    }
    
    console.log(`💾 Rating movie ${currentMovieId} with ${currentRating} stars`);
    
    // Show loading state
    $('#rateMovieBtn').prop('disabled', true).html('<i class="bi bi-hourglass-split"></i> Đang lưu...');
    
    // Make AJAX request
    $.ajax({
        url: '/rate_movie',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            movieId: currentMovieId,
            rating: currentRating
        }),
        success: function(response) {
            console.log('✅ Rating saved:', response);
            
            // Update personalized recommendations
            if (response.personalized) {
                displayMovieCarousel(
                    'personalized', 
                    response.personalized, 
                    '#personalizedMoviesContainer', 
                    '#personalizedMoviesEmpty'
                );
            }
            
            // Show success message
            alert(response.message || 'Đã lưu đánh giá thành công!');
            
            // Close modal
            $('#movieDetailModal').modal('hide');
            
            // Reset button state
            $('#rateMovieBtn').prop('disabled', false).html('<i class="bi bi-check-circle"></i> Đã Xem - Lưu Đánh Giá');
            
            // Scroll to personalized section
            $('html, body').animate({
                scrollTop: $('#personalizedMoviesCarousel').offset().top - 150
            }, 500);
        },
        error: function(xhr, status, error) {
            console.error('❌ Rating failed:', error);
            
            const errorMsg = xhr.responseJSON?.error || 'Lỗi khi lưu đánh giá. Vui lòng thử lại!';
            alert(errorMsg);
            
            // Reset button state
            $('#rateMovieBtn').prop('disabled', false).html('<i class="bi bi-check-circle"></i> Đã Xem - Lưu Đánh Giá');
        }
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

/**
 * Make showMovieDetail function globally accessible
 */
window.showMovieDetail = showMovieDetail;

// ============================================================================
// FLEXIBLE SEARCH MODE - FILTER SYSTEM
// ============================================================================

/**
 * Load filter data from backend
 */
function loadFilterData() {
    console.log('🔄 Loading filter data...');
    
    $.ajax({
        url: '/filter_data',
        method: 'GET',
        success: function(data) {
            console.log('✅ Filter data loaded:', data);
            filterData = data;
            populateFilterTags();
        },
        error: function(xhr, status, error) {
            console.error('❌ Failed to load filter data:', error);
            alert('Không thể tải dữ liệu bộ lọc. Vui lòng thử lại!');
        }
    });
}

/**
 * Populate all filter tags
 */
function populateFilterTags() {
    if (!filterData) {
        console.error('❌ No filter data available');
        return;
    }
    
    // Populate Countries
    const $countriesTags = $('#countriesTags');
    $countriesTags.empty();
    if (filterData.production_countries && filterData.production_countries.length > 0) {
        filterData.production_countries.forEach(country => {
            $countriesTags.append(
                `<span class="filter-tag" data-type="country" data-value="${escapeHtml(country)}">
                    ${escapeHtml(country)}
                </span>`
            );
        });
    }
    
    // Populate Genres
    const $genresTags = $('#genresTags');
    $genresTags.empty();
    if (filterData.genres && filterData.genres.length > 0) {
        filterData.genres.forEach(genre => {
            $genresTags.append(
                `<span class="filter-tag" data-type="genre" data-value="${escapeHtml(genre)}">
                    ${escapeHtml(genre)}
                </span>`
            );
        });
    }
    
    // Populate Years
    const $yearsTags = $('#yearsTags');
    $yearsTags.empty();
    if (filterData.release_years && filterData.release_years.length > 0) {
        filterData.release_years.forEach(year => {
            $yearsTags.append(
                `<span class="filter-tag" data-type="year" data-value="${year}">
                    ${year}
                </span>`
            );
        });
    }
    
    // Populate Sort Options (SINGLE SELECT)
    const $sortOptions = $('#sortOptions');
    $sortOptions.empty();
    if (filterData.sort_options && filterData.sort_options.length > 0) {
        filterData.sort_options.forEach(option => {
            $sortOptions.append(
                `<span class="filter-tag" data-type="sort" data-value="${escapeHtml(option.value)}">
                    ${escapeHtml(option.label)}
                </span>`
            );
        });
    }
    
    console.log(`✅ Populated: ${filterData.production_countries?.length || 0} countries, ` +
                `${filterData.genres?.length || 0} genres, ` +
                `${filterData.release_years?.length || 0} years, ` +
                `${filterData.sort_options?.length || 0} sort options`);
}

/**
 * Handle filter section toggle (collapsible)
 */
function handleFilterSectionToggle(e) {
    const $header = $(e.currentTarget);
    const $content = $header.next('.filter-section-content');
    const $icon = $header.find('.filter-section-icon');
    
    // Toggle show class
    $content.toggleClass('show');
    
    // Toggle icon rotation
    $icon.toggleClass('expanded');
}

/**
 * Handle filter tag click
 */
function handleFilterTagClick(e) {
    const $tag = $(e.currentTarget);
    const tagType = $tag.data('type');
    
    // Special handling for SORT (single select)
    if (tagType === 'sort') {
        // Deactivate all other sort tags
        $('.filter-tag[data-type="sort"]').removeClass('active');
    }
    
    // Toggle active state
    $tag.toggleClass('active');
    
    console.log(`🏷️ Tag clicked: ${$tag.data('value')} (type: ${tagType})`);
}

/**
 * Handle apply filters button click
 */
function handleApplyFilters() {
    // Collect active filters
    const filters = {
        search_query: $('#flexibleSearchInput').val().trim(),
        countries: [],
        genres: [],
        years: [],
        sort_by: 'popularity' // Default
    };
    
    // Collect active countries
    $('.filter-tag[data-type="country"].active').each(function() {
        filters.countries.push($(this).data('value'));
    });
    
    // Collect active genres
    $('.filter-tag[data-type="genre"].active').each(function() {
        filters.genres.push($(this).data('value'));
    });
    
    // Collect active years
    $('.filter-tag[data-type="year"].active').each(function() {
        filters.years.push($(this).data('value'));
    });
    
    // Collect active sort (should be only 1)
    const $activeSort = $('.filter-tag[data-type="sort"].active');
    if ($activeSort.length > 0) {
        filters.sort_by = $activeSort.data('value');
    }
    
    console.log('🔍 Applying filters:', filters);
    
    // Show loading spinner
    $('#filterLoadingSpinner').show();
    $('#filterResultsContainer').hide();
    
    // Make AJAX request
    $.ajax({
        url: '/filter',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(filters),
        success: function(response) {
            console.log('✅ Filter results:', response);
            
            // Hide loading
            $('#filterLoadingSpinner').hide();
            
            // Display results
            displayFilterResults(response);
            
            // Show results container
            $('#filterResultsContainer').show();
            
            // Smooth scroll to results
            $('html, body').animate({
                scrollTop: $('#filterResultsContainer').offset().top - 100
            }, 500);
        },
        error: function(xhr, status, error) {
            console.error('❌ Filter failed:', error);
            
            $('#filterLoadingSpinner').hide();
            
            const errorMsg = xhr.responseJSON?.error || 'Lỗi khi lọc phim. Vui lòng thử lại!';
            alert(errorMsg);
        }
    });
}

/**
 * Display filter results across 3 pagination sections
 */
function displayFilterResults(data) {
    const movies = data.movies || [];
    const total = data.total || 0;
    
    // Update total count
    $('#totalResultsCount').text(total);
    
    // Split movies into 3 groups (10 each)
    const group1 = movies.slice(0, 10);
    const group2 = movies.slice(10, 20);
    const group3 = movies.slice(20, 30);
    
    // Display each group
    displayFilterSection(group1, '#filterResults1', '#pagination1', 1);
    displayFilterSection(group2, '#filterResults2', '#pagination2', 2);
    displayFilterSection(group3, '#filterResults3', '#pagination3', 3);
    
    console.log(`✅ Displayed ${movies.length} movies across 3 sections`);
}

/**
 * Display movies in a single filter section
 */
function displayFilterSection(movies, containerSelector, paginationSelector, sectionNum) {
    const $container = $(containerSelector);
    const $pagination = $(paginationSelector);
    
    // Clear previous content
    $container.empty();
    $pagination.empty();
    
    // Check if movies exist
    if (!movies || movies.length === 0) {
        $container.html('<p class="text-center text-muted">Không có phim nào</p>');
        return;
    }
    
    // Display all movies in this section (no pagination within section)
    movies.forEach(movie => {
        $container.append(createMovieCard(movie));
    });
    
    console.log(`✅ Section ${sectionNum}: Displayed ${movies.length} movies`);
}

/**
 * Handle clear filters button click
 */
function handleClearFilters() {
    // Deactivate all tags
    $('.filter-tag').removeClass('active');
    
    // Clear search input
    $('#flexibleSearchInput').val('');
    
    // Hide results
    $('#filterResultsContainer').hide();
    
    // Reset total count
    $('#totalResultsCount').text('0');
    
    console.log('🧹 Filters cleared');
}
