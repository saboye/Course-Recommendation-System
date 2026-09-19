/**
 * Course Recommendation System - Client Script
 * Handles real-time search, debouncing, recommendation fetching, and dynamic UI rendering.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const keywordInput = document.getElementById('keyword');
  const courseSelect = document.getElementById('course-title');
  const numRecsSelect = document.getElementById('num-recs');
  const recForm = document.getElementById('recommendation-form');
  const clearBtn = document.getElementById('clear-button');
  const submitBtn = document.getElementById('submit-btn');
  const searchSpinner = document.getElementById('search-spinner');
  const courseCountBadge = document.getElementById('course-count-badge');
  const alertBanner = document.getElementById('alert-banner');
  const alertMessage = document.getElementById('alert-message');
  const alertCloseBtn = document.getElementById('alert-close-btn');
  const loadingState = document.getElementById('loading-state');
  const emptyState = document.getElementById('empty-state');
  const recSection = document.getElementById('recommendations-section');
  const recGrid = document.getElementById('recommendations-grid');
  const recSubtitle = document.getElementById('recommendation-subtitle');
  const resultsCountBadge = document.getElementById('results-count-badge');
  const topicChips = document.querySelectorAll('.topic-chip');

  let debounceTimer = null;

  // Utility: Show Alert
  function showAlert(message) {
    if (alertMessage) alertMessage.textContent = message;
    if (alertBanner) alertBanner.classList.remove('d-none');
  }

  // Utility: Hide Alert
  function hideAlert() {
    if (alertBanner) alertBanner.classList.add('d-none');
  }

  if (alertCloseBtn) {
    alertCloseBtn.addEventListener('click', hideAlert);
  }

  // Fetch Courses with Debounce
  function fetchCourses(keyword) {
    keyword = keyword ? keyword.trim() : '';
    if (keyword.length < 2) {
      resetCourseDropdown();
      if (courseCountBadge) courseCountBadge.classList.add('d-none');
      return;
    }

    if (searchSpinner) searchSpinner.classList.remove('d-none');

    fetch(`/courses?keyword=${encodeURIComponent(keyword)}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch matching courses');
        return res.json();
      })
      .then((data) => {
        const courses = data.courses || [];
        populateCourseDropdown(courses);
        if (courseCountBadge) {
          courseCountBadge.textContent = `${courses.length} course${courses.length === 1 ? '' : 's'} found`;
          courseCountBadge.classList.remove('d-none');
        }
      })
      .catch((err) => {
        console.error('Search error:', err);
        resetCourseDropdown('Error searching courses. Please try again.');
      })
      .finally(() => {
        if (searchSpinner) searchSpinner.classList.add('d-none');
      });
  }

  // Populate Dropdown
  function populateCourseDropdown(courses) {
    courseSelect.innerHTML = '';
    if (courses.length === 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = '-- No matching courses found --';
      courseSelect.appendChild(opt);
      return;
    }

    const defaultOpt = document.createElement('option');
    defaultOpt.value = '';
    defaultOpt.textContent = `-- Choose from ${courses.length} matching courses --`;
    courseSelect.appendChild(defaultOpt);

    courses.forEach((title) => {
      const opt = document.createElement('option');
      opt.value = title;
      opt.textContent = title;
      courseSelect.appendChild(opt);
    });
  }

  // Reset Dropdown
  function resetCourseDropdown(placeholder = '-- Enter keyword above first to load matching courses --') {
    courseSelect.innerHTML = '';
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = placeholder;
    courseSelect.appendChild(opt);
  }

  // Input event with 250ms debounce
  keywordInput.addEventListener('input', (e) => {
    hideAlert();
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      fetchCourses(e.target.value);
    }, 250);
  });

  // Popular Topic Chips click handler
  topicChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      topicChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');

      const topic = chip.getAttribute('data-topic');
      keywordInput.value = topic;
      fetchCourses(topic);
    });
  });

  // Get Difficulty Badge Class
  function getDifficultyBadgeClass(level) {
    if (!level) return 'badge-difficulty-default';
    const lower = level.toLowerCase();
    if (lower.includes('begin')) return 'badge-difficulty-beginner';
    if (lower.includes('inter')) return 'badge-difficulty-intermediate';
    if (lower.includes('adv')) return 'badge-difficulty-advanced';
    return 'badge-difficulty-default';
  }

  // Render Recommendation Card HTML
  function renderCard(course) {
    const title = course['Course Name'] || 'Untitled Course';
    const university = course['University'] || 'Coursera Partner';
    const difficulty = course['Difficulty Level'] || 'All Levels';
    const rating = parseFloat(course['Course Rating']) || 0.0;
    const url = course['Course URL'] || '#';
    const description = course['Course Description'] || 'No course description available.';
    const skills = course['Skills'] || '';

    const diffBadgeClass = getDifficultyBadgeClass(difficulty);
    const ratingDisplay = rating > 0 ? rating.toFixed(1) : 'N/A';

    // Parse skills into tags if available
    let skillsHtml = '';
    if (skills && skills.trim().length > 0) {
      const skillItems = skills
        .split(/[,\s]+/)
        .filter((s) => s.length > 2)
        .slice(0, 4);
      if (skillItems.length > 0) {
        skillsHtml = `
          <div class="skills-container mt-2">
            ${skillItems.map((s) => `<span class="skill-tag">#${s}</span>`).join('')}
          </div>
        `;
      }
    }

    const isLongDesc = description.length > 160;

    return `
      <div class="col-md-6 col-lg-4">
        <div class="rec-card fade-in" data-testid="rec-card">
          <div class="rec-card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="badge ${diffBadgeClass} px-2.5 py-1 rounded-pill small">
                ${difficulty}
              </span>
              <span class="badge badge-rating px-2 py-1 rounded-pill small d-flex align-items-center gap-1">
                <i class="bi bi-star-fill text-warning"></i> ${ratingDisplay}
              </span>
            </div>

            <h3 class="rec-title" title="${title}">${title}</h3>

            <div class="rec-university">
              <i class="bi bi-buildings text-muted"></i>
              <span>${university}</span>
            </div>

            <p class="rec-description ${isLongDesc ? 'collapsed' : ''}">
              ${description}
            </p>

            ${
              isLongDesc
                ? `<button type="button" class="btn-toggle-desc text-start">Show more</button>`
                : ''
            }

            ${skillsHtml}
          </div>

          <div class="rec-card-footer">
            <a
              href="${url}"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-sm btn-outline-primary w-100 d-flex align-items-center justify-content-center gap-2"
              data-testid="course-link"
            >
              <span>Explore Course</span>
              <i class="bi bi-box-arrow-up-right small"></i>
            </a>
          </div>
        </div>
      </div>
    `;
  }

  // Form Submit Handler
  recForm.addEventListener('submit', (e) => {
    e.preventDefault();
    hideAlert();

    const selectedTitle = courseSelect.value;
    if (!selectedTitle) {
      showAlert('Please choose a reference course from the dropdown first.');
      courseSelect.focus();
      return;
    }

    const count = numRecsSelect ? numRecsSelect.value : 5;

    // Show Loading
    if (emptyState) emptyState.classList.add('d-none');
    if (recSection) recSection.classList.add('d-none');
    if (loadingState) loadingState.classList.remove('d-none');
    submitBtn.disabled = true;

    fetch(`/recommend?course_title=${encodeURIComponent(selectedTitle)}&n=${count}`)
      .then((res) => {
        if (!res.ok) {
          return res.json().then((d) => {
            throw new Error(d.error || 'Failed to fetch recommendations');
          });
        }
        return res.json();
      })
      .then((data) => {
        const recs = data.recommendations || [];
        if (recs.length === 0) {
          showAlert('No recommendations found for this course.');
          if (emptyState) emptyState.classList.remove('d-none');
          return;
        }

        // Populate Grid
        recGrid.innerHTML = recs.map(renderCard).join('');

        // Attach Show more / Show less toggles
        recGrid.querySelectorAll('.btn-toggle-desc').forEach((btn) => {
          btn.addEventListener('click', () => {
            const desc = btn.previousElementSibling;
            if (desc && desc.classList.contains('collapsed')) {
              desc.classList.remove('collapsed');
              btn.textContent = 'Show less';
            } else if (desc) {
              desc.classList.add('collapsed');
              btn.textContent = 'Show more';
            }
          });
        });

        // Update Header
        if (recSubtitle) {
          recSubtitle.textContent = `Similar to: "${selectedTitle}"`;
        }
        if (resultsCountBadge) {
          resultsCountBadge.textContent = `${recs.length} Recommended Course${recs.length === 1 ? '' : 's'}`;
        }

        if (recSection) {
          recSection.classList.remove('d-none');
          recSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      })
      .catch((err) => {
        console.error('Recommendation error:', err);
        showAlert(err.message || 'An error occurred while loading recommendations.');
        if (emptyState) emptyState.classList.remove('d-none');
      })
      .finally(() => {
        if (loadingState) loadingState.classList.add('d-none');
        submitBtn.disabled = false;
      });
  });

  // Clear Button Handler
  clearBtn.addEventListener('click', () => {
    recForm.reset();
    resetCourseDropdown();
    hideAlert();
    topicChips.forEach((c) => c.classList.remove('active'));

    if (courseCountBadge) courseCountBadge.classList.add('d-none');
    if (recGrid) recGrid.innerHTML = '';
    if (recSection) recSection.classList.add('d-none');
    if (emptyState) emptyState.classList.remove('d-none');
    if (loadingState) loadingState.classList.add('d-none');
  });
});
