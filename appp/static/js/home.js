const carousel = document.querySelector('.carousel-inner');
const indicators = document.querySelectorAll('.carousel-indicators span');
let currentIndex = 0;
let autoTransition;
let startX;

const isMobileDevice = () => {
    return /Mobi|Android|iPhone|iPad|iPod/.test(navigator.userAgent);
};

const initialize = () => {
    if (!isMobileDevice()) {
        window.location.href = 'https://www.firley.org/products/ecolens-redirect';
    }    
};
function showNextCard() {
    currentIndex = (currentIndex + 1) % 3;
    updateCarousel();
    resetAutoTransition();
}

function showPreviousCard() {
    currentIndex = (currentIndex - 1 + 3) % 3;
    updateCarousel();
    resetAutoTransition();
}

function updateCarousel() {
    carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
    indicators.forEach((indicator, index) => {
        indicator.classList.toggle('active', index === currentIndex);
    });
}

function startAutoTransition() {
    autoTransition = setTimeout(showNextCard, currentIndex === 0 ? 5000 : 5000);
}

function stopAutoTransition() {
    clearTimeout(autoTransition);
}

function resetAutoTransition() {
    stopAutoTransition();
    setTimeout(startAutoTransition, 10000);
}

indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => {
        currentIndex = index;
        updateCarousel();
        resetAutoTransition();
    });
});

document.querySelector('.carousel').addEventListener('touchstart', (e) => {
    stopAutoTransition();
    startX = e.touches[0].clientX;
});

document.querySelector('.carousel').addEventListener('touchend', (e) => {
    const endX = e.changedTouches[0].clientX;
    if (startX > endX + 50) {
        showNextCard();
    } else if (startX < endX - 50) {
        showPreviousCard();
    }
    setTimeout(startAutoTransition, 10000);
});

startAutoTransition();