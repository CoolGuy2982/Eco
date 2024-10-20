document.addEventListener('DOMContentLoaded', function () {
    const levelGoals = [50, 110, 220, 350, 500, 650, 800, 950, 1100, 1300];
    const levelColors = ['#a8f28a', '#87CEEB', '#f2994a', '#eb5757', '#6fcf97', '#56ccf2', '#bb6bd9', '#2f80ed', '#9b51e0', '#27ae60'];
    const levelImages = [
            'static/images/trees/level0.png',
            'static/images/trees/level1.png',
            'static/images/trees/level2.png',
            'static/images/trees/level3.png',
            'static/images/trees/level4.png',
            'static/images/trees/level5.png',
            'static/images/trees/level6.png',
            'static/images/trees/level7.png',
            'static/images/trees/level8.png',
            'static/images/trees/level9.png',
            'static/images/trees/level10.png',
        ];

    const ecoPoints = localStorage.getItem('ecoPoints') ? parseInt(localStorage.getItem('ecoPoints')) : 0;
    let level = localStorage.getItem('level') ? parseInt(localStorage.getItem('level')) : 0;

    const treeName = localStorage.getItem('treeName') || 'Your Tree';
    document.getElementById('treeName').innerText = treeName;

    function updateProgress() {
        const progressCircle = document.getElementById('progressCircle');
        const levelText = document.getElementById('treeLevel');
        const treeImage = document.getElementById('treeImage');
        const nextLevelPoints = levelGoals[level] || 150;

        let progress = (ecoPoints / nextLevelPoints) * 100;
        if (progress > 100) progress = 100;

        const radius = progressCircle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (progress / 100) * circumference;
        progressCircle.style.strokeDasharray = `${circumference}`;
        progressCircle.style.strokeDashoffset = `${offset}`;
        progressCircle.style.stroke = levelColors[level] || '#a8f28a';
        
        levelText.innerText = `Lvl ${level}`;
        treeImage.src = levelImages[level] || levelImages[0];
        document.getElementById('ecoPointsButton').innerText = `${ecoPoints} EcoPoints`;
    }

    document.getElementById('treeProgress').addEventListener('click', function () {
        window.location.href = '/ecopoints';
    });
    updateProgress();

    let pastResponses = JSON.parse(localStorage.getItem('pastResponses')) || [];
    const container = document.querySelector('.recent-scans');

    pastResponses.reverse().forEach((response, index) => {
        if (response.b64_image) {
            const link = document.createElement('a');
            link.href = `/past-responses#response-${index}`;
            link.className = 'scan-item';
            link.innerHTML = `<img src="data:image/png;base64,${response.b64_image}" alt="Response ${index}" class="scan-image">`;
            container.appendChild(link);
        }
    });
});

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
        window.location.href = 'https://www.firley.net/products/ecolens-redirect';
    }
};

initialize();

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

document.addEventListener('DOMContentLoaded', function() {
function isIOS() {
return /iphone|ipod|ipad/.test(window.navigator.userAgent.toLowerCase());
}

function isInStandaloneMode() {
return ('standalone' in window.navigator) && (window.navigator.standalone);
}

var dismissed = localStorage.getItem('addToHomeScreenDismissed');

if (isIOS() && !isInStandaloneMode() && !dismissed) {
showPopup();
}
});

function showPopup() {
document.getElementById('addToHomeScreen').style.display = 'block';
document.getElementById('subscriptionPopup').style.display = 'block';
}

function closePopup() {
document.getElementById('addToHomeScreen').style.display = 'none';
localStorage.setItem('addToHomeScreenDismissed', 'true');
}


startAutoTransition();


function isIos() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

function isInStandaloneMode() {
    return ('standalone' in window.navigator) && (window.navigator.standalone);
}

function shouldShowPopup() {
    return isIos() && !isInStandaloneMode() && !localStorage.getItem('popupShown');
}

if (shouldShowPopup()) {
    document.getElementById('popup').style.display = 'block';
    document.getElementById('triangle-container').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
    localStorage.setItem('popupShown', 'true');
}

document.getElementById('closeButton').onclick = function() {
    document.getElementById('popup').style.display = 'none';
    document.getElementById('triangle-container').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}