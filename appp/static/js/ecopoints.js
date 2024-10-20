let ecoPoints = localStorage.getItem('ecoPoints') ? parseInt(localStorage.getItem('ecoPoints')) : 0;
let level = localStorage.getItem('level') ? parseInt(localStorage.getItem('level')) : 0;

const goals = [50, 110, 220, 350, 500, 650, 800, 950, 1100, 1300];
const rewards = [
    [
        { 
            name: "Free Ecoternatives Floss", 
            cardImage: "https://ecoternatives.co/cdn/shop/files/The_World_s_Most_5.png?crop=center&height=32&v=1708425732&width=32", 
            popupImage: "https://ecoternatives.co/cdn/shop/files/Screenshot_2024-02-20_at_8.48.00_PM_3.png?v=1708426636&width=230", 
            code: "FREEFLOSS (Order $35+)", 
            link: "https://ecoternatives.co/products/strong-bamboo-floss" 
        },
        { 
            name: "Exclusive Eco Wallpaper", 
            cardImage: "https://lh3.googleusercontent.com/pw/AP1GczO6Sem5UzEvBOtQhjpetfwM4PzuQK0PFpp-NpyWco9PHzXGeWfp1GnKHO6A7gm3jy2Ek1cNE3CNMsKoivnd4EQ9ZFN4Q2cC04o4Lq2cfXQAMcJCOIsxZ6kQxus2LbU5hi1d7MRNFmnJsEmwECPBU6aB=w1598-h913-s-no-gm?authuser=0", 
            popupImage: "https://lh3.googleusercontent.com/pw/AP1GczO6Sem5UzEvBOtQhjpetfwM4PzuQK0PFpp-NpyWco9PHzXGeWfp1GnKHO6A7gm3jy2Ek1cNE3CNMsKoivnd4EQ9ZFN4Q2cC04o4Lq2cfXQAMcJCOIsxZ6kQxus2LbU5hi1d7MRNFmnJsEmwECPBU6aB=w1598-h913-s-no-gm?authuser=0", 
            code: "Enjoy :) [tap the picture ^^]", 
            link: "https://photos.google.com/share/AF1QipOt6VJARXqi0qUa65Cv6PAQIKj78CwSvOd5uYSGqYfpLzGQBbwigfp6nl5zbIZsJQ/photo/AF1QipPHy7iYaeS2PEEk_9A_Dmw3FzYXYqkalRt36s-c?key=TDdDZjQ5Umd3ekxqOWF6V3NxOV9BMGU4aGZKLVJn" 
        },
    ],
    [
        { 
            name: "50% Off Terra Thread Apparel", 
            cardImage: "https://cdn.pushowl.com/images/tr:cm-pad_resize,w-192,h-192,bg-FFFFFF00/terra-thread/default-c2c03e44-0acc-47da-8ad5-6f63e87cb764-TerraThreadLogo.png?ik-sdk-version=python-2.2.4&ik-t=9999999999&ik-s=ba9432aaf4a4be2f0c75ae7b27d60b15338fd470", 
            popupImage: "https://d13wriz42ny3t5.cloudfront.net/production/2020/11/06111407/TerraThread_Banner2.jpg?width=1000", 
            code: "Tap the picture above ^", 
            link: "https://terrathread.com/" 
        },
        { 
            name: "Eco Ebook - Ethan [Exclusive]", 
            cardImage: "static/images/rewards/ethan_cover.png", 
            popupImage: "static/images/rewards/ethan_cover.png", 
            code: "Tap the image", 
            link: "https://drive.google.com/file/d/1xk0DpMogSUhTWiNRxBYT7f4Y9xJBUzZP/view?usp=sharing" 
        },
    ],
    [
        { 
            name: "10% Off Lochtree", 
            cardImage: "https://lochtree.com/cdn/shop/files/Favicon-2_fdf9acae-7925-42b3-a0bf-18cc3b6548cc_180x180.png?v=1651499050", 
            popupImage: "static/images/rewards/lochtree.png", 
            code: "WELCOME-10", 
            link: "https://lochtree.com" 
        },
        { 
            name: "Exclusive Env Book Club [Secret]", 
            cardImage: "static/images/rewards/spark_logo.png", 
            popupImage: "static/images/rewards/spark_logo.png", 
            code: "Tap the pic ^", 
            link: "https://sites.google.com/view/sparkfirley/spark" 
        },
    ],
    // levels 4-10 gift cards with "Coming Soon"
    [
        { 
            name: "Coming Soon", 
            cardImage: "", 
            popupImage: "", 
            code: "Coming Soon lol", 
            link: "" 
        },
    ]
];
let claimedRewards = {};

function updateUI() {
    document.getElementById('ecoPointsDisplay').textContent = ecoPoints;
    document.getElementById('currentLevel').textContent = level;
    document.getElementById('currentTreeImage').src = `static/images/trees/level${level}.png`;

    const nextLevel = level + 1;
    document.getElementById('nextLevel').textContent = nextLevel;
    document.getElementById('nextTreeImage').src = `static/images/trees/level${nextLevel}.png`;

    const progressPercentage = ((ecoPoints|| 0)) / (goals[level]  || 0) * 100;
    document.getElementById('progressBar').style.width = `${Math.min(progressPercentage, 100)}%`;

    const currentRewardsList = document.getElementById('currentRewards');
    currentRewardsList.innerHTML = "";
    rewards[level].forEach((reward, index) => {
        const li = document.createElement('li');
        const img = document.createElement('img');
        img.src = reward.cardImage;
        li.appendChild(img);
        li.appendChild(document.createTextNode(reward.name));
        const claimButton = document.createElement('button');
        claimButton.className = 'claim-button';
        claimButton.textContent = 'Claim';
        claimButton.onclick = (event) => {
            event.stopPropagation();
            showPopup(reward, index);
        };
        li.appendChild(claimButton);
        if (claimedRewards[level] && claimedRewards[level][index]) {
            claimButton.style.display = 'none';
        }
        li.onclick = () => showPopup(reward, index);
        currentRewardsList.appendChild(li);
    });

    const upgradeButton = document.getElementById('upgradeButton');
    if (ecoPoints >= goals[level]) { // needs correct comparison for the next level
        upgradeButton.classList.remove('disabled');
        upgradeButton.disabled = false;
    } else {
        upgradeButton.classList.add('disabled');
        upgradeButton.disabled = true;
    }
}

function upgradeTree() {
    const nextLevel = level + 1;
    if (ecoPoints >= goals[level]) { 
        level = nextLevel;
        localStorage.setItem('level', level);
        alert(`You've upgraded to level ${level}!`);
        updateUI();
    }
}

function showUpcomingRewards() {
    const nextLevel = level + 1;
    const upcomingRewardsList = document.getElementById('upcomingRewardsList');
    upcomingRewardsList.innerHTML = "";
    rewards[nextLevel].forEach(reward => {
        const li = document.createElement('li');
        const img = document.createElement('img');
        img.src = reward.cardImage;
        li.appendChild(img);
        li.appendChild(document.createTextNode(reward.name));
        upcomingRewardsList.appendChild(li);
    });
    document.getElementById('upcomingRewards').style.display = 'block';
}

function setEcoPoints() {
    const ecoPointsInput = document.getElementById('ecoPointsInput').value;
    ecoPoints = parseInt(ecoPointsInput, 10);
    localStorage.setItem('ecoPoints', ecoPoints);
    updateUI();
}

function showPopup(reward, index) {
    document.getElementById('rewardName').textContent = reward.name;
    document.getElementById('rewardImage').src = reward.popupImage;
    document.getElementById('popupOverlay').style.display = 'flex';

    document.getElementById('rewardImage').onclick = () => {
        window.location.href = reward.link;
    };

    if (reward.code === "COMING_SOON") {
        document.getElementById('claimButton').style.display = 'none';
        document.getElementById('claimedCode').style.display = 'block';
        document.getElementById('rewardCode').textContent = "Coming Soon!";
        document.getElementById('screenshotMessage').textContent = "";
    } else {
        document.getElementById('claimButton').style.display = 'block';
        document.getElementById('claimedCode').style.display = 'none';
        document.getElementById('claimButton').onclick = () => claimReward(reward, index);
    }

    if (claimedRewards[level] && claimedRewards[level][index]) {
        document.getElementById('claimButton').style.display = 'none';
        document.getElementById('rewardCode').textContent = `Reward Code: ${reward.code}`;
        document.getElementById('claimedCode').style.display = 'block';
        document.getElementById('screenshotMessage').textContent = "Take a screenshot! Tap the photo";
    }
}

function closePopup() {
    document.getElementById('popupOverlay').style.display = 'none';
}

function claimReward(reward, index) {
    if (!claimedRewards[level]) {
        claimedRewards[level] = {};
    }
    claimedRewards[level][index] = true;
    localStorage.setItem('claimedRewards', JSON.stringify(claimedRewards));

    document.getElementById('claimButton').style.display = 'none';
    document.getElementById('rewardCode').textContent = `Reward Code: ${reward.code}`;
    document.getElementById('claimedCode').style.display = 'block';
    document.getElementById('screenshotMessage').textContent = "Take a screenshot! Tap the picture above.";

    const confetti = document.getElementById('confetti');
    confetti.style.display = 'block';
    setTimeout(() => {
        confetti.style.display = 'none';
    }, 3000);

    startConfetti();
    updateUI();
}

function startConfetti() {
    const duration = 3 * 1000;
    const end = Date.now() + duration;

    (function frame() {
        confetti({
            particleCount: 2,
            angle: 60,
            spread: 55,
            origin: { x: 0 }
        });
        confetti({
            particleCount: 2,
            angle: 120,
            spread: 55,
            origin: { x: 1 }
        });

        if (Date.now() < end) {
            requestAnimationFrame(frame);
        }
    }());
}

if (localStorage.getItem('claimedRewards')) {
    claimedRewards = JSON.parse(localStorage.getItem('claimedRewards'));
}

updateUI();

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
};
