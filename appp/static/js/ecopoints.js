let ecoPoints = localStorage.getItem('ecoPoints') ? parseInt(localStorage.getItem('ecoPoints')) : 0;
        let level = localStorage.getItem('level') ? parseInt(localStorage.getItem('level')) : 0;

        const goals = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]; // Goals for each level
        const rewards = [
            [
                { name: "10% Off Lochtree ", cardImage: "static/images/rewards/lochtree.png", popupImage: "static/images/rewards/lochtree.png", code: "WELCOME-10" },
                { name: "15% Off Terra Thread", cardImage: "https://d13wriz42ny3t5.cloudfront.net/production/2020/11/06111407/TerraThread_Banner2.jpg?width=1000", popupImage: "https://earthhero.com/cdn/shop/files/1D6042-logomark-and-wordmark_400x.png?v=1657915460", code: "" },
                { name: "Free Ecoternatives Floss (Order $35+)", cardImage: "https://ecoternatives.co/cdn/shop/files/Screenshot_2024-02-20_at_8.48.00_PM_3.png?v=1708426636&width=230", popupImage: "https://ecoternatives.co/cdn/shop/files/Screenshot_2024-02-20_at_8.48.00_PM_3.png?v=1708426636&width=230", code: "FREEFLOSS " }
            ],
            [
                { name: "Coupon 4", cardImage: "static/images/rewards/coupon4_card.png", popupImage: "static/images/rewards/coupon4.png", code: "CPN1234" },
                { name: "Coupon 5", cardImage: "static/images/rewards/coupon5_card.png", popupImage: "static/images/rewards/coupon5.png", code: "CPN4567" },
                { name: "Coupon 6", cardImage: "static/images/rewards/coupon6_card.png", popupImage: "static/images/rewards/coupon6.png", code: "CPN7890" }
            ],
            [
                { name: "Coupon 7", cardImage: "static/images/rewards/coupon7_card.png", popupImage: "static/images/rewards/coupon7.png", code: "CPN12345" },
                { name: "Coupon 8", cardImage: "static/images/rewards/coupon8_card.png", popupImage: "static/images/rewards/coupon8.png", code: "CPN45678" },
                { name: "Coupon 9", cardImage: "static/images/rewards/coupon9_card.png", popupImage: "static/images/rewards/coupon9.png", code: "CPN78901" }
            ],
            // Levels 4-10 gift cards with "Coming Soon"
            [
                { name: "$20 Amazon Gift Card", cardImage: "static/images/rewards/amazon_gift_card_card.png", popupImage: "static/images/rewards/amazon_gift_card.png", code: "COMING_SOON" },
                { name: "$15 Starbucks Gift Card", cardImage: "static/images/rewards/starbucks_gift_card_card.png", popupImage: "static/images/rewards/starbucks_gift_card.png", code: "COMING_SOON" },
                { name: "6 Month Netflix Subscription", cardImage: "static/images/rewards/netflix_subscription_card.png", popupImage: "static/images/rewards/netflix_subscription.png", code: "COMING_SOON" }
            ]
            // Add more rewards as needed
        ];
        let claimedRewards = {};

        function updateUI() {
    document.getElementById('ecoPointsDisplay').textContent = ecoPoints;
    document.getElementById('currentLevel').textContent = level;
    document.getElementById('currentTreeImage').src = `static/images/trees/level${level}.png`;

    const nextLevel = level + 1;
    document.getElementById('nextLevel').textContent = nextLevel;
    document.getElementById('nextTreeImage').src = `static/images/trees/level${nextLevel}.png`;

    const progressPercentage = ((ecoPoints - (goals[level - 1] || 0)) / (goals[level] - (goals[level - 1] || 0))) * 100;
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
    if (ecoPoints >= goals[level]) { // Correct comparison for the next level
        upgradeButton.classList.remove('disabled');
        upgradeButton.disabled = false;
    } else {
        upgradeButton.classList.add('disabled');
        upgradeButton.disabled = true;
    }
}

function upgradeTree() {
    const nextLevel = level + 1;
    if (ecoPoints >= goals[level]) { // Correct comparison for the next level
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
                document.getElementById('screenshotMessage').textContent = "Take a screenshot!";
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
            document.getElementById('screenshotMessage').textContent = "Take a screenshot!";

            // Show confetti
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

        // Load claimed rewards from localStorage
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
      }