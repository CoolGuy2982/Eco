// JavaScript code to process image and handle the analysis page

function saveResponseLocally(data) {
  try {
      let pastResponses = JSON.parse(localStorage.getItem('pastResponses')) || [];
      const existingIndex = pastResponses.findIndex(response => response.date === data.date);

      if (existingIndex > -1) {
          pastResponses[existingIndex] = { ...pastResponses[existingIndex], ...data };
      } else {
          pastResponses.push(data);
      }

      try {
          localStorage.setItem('pastResponses', JSON.stringify(pastResponses));
      } catch (error) {
          if (error.code === 22) {
              console.warn('Quota exceeded, removing oldest entries');
              while (error.code === 22 && pastResponses.length > 0) {
                  pastResponses.shift();
                  try {
                      localStorage.setItem('pastResponses', JSON.stringify(pastResponses));
                      error = null;
                  } catch (e) {
                      error = e;
                  }
              }
          }
      }
  } catch (error) {
      console.error('Error saving response locally:', error);
      displayError('Error saving response locally: ' + error.message);
  }
}

function getEcoPoint() {
  return parseInt(localStorage.getItem('ecoPoints') || '0', 10);
}

function incrementEcoPoint() {
  let ecoPoint = getEcoPoint();
  ecoPoint += 1;
  localStorage.setItem('ecoPoints', ecoPoint.toString());
  displayEcoPoint();
}

function displayEcoPoint() {
  let ecoPoint = getEcoPoint();
  const ecoPointElement = document.getElementById('eco-point');
  ecoPointElement.textContent = '+1 EcoPoint';
  ecoPointElement.classList.add('visible');

  setTimeout(() => {
      ecoPointElement.classList.remove('visible');
  }, 3000); 
}

function fetchAddressAndDisplay(keyword, data) {
  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
          position => {
              const latitude = position.coords.latitude;
              const longitude = position.coords.longitude;
              const keywordString = encodeURIComponent(keyword);
              const url = `/scrape_address?what=${keywordString}&latitude=${latitude}&longitude=${longitude}`;

              fetch(url)
                  .then(response => response.json())
                  .then(addressData => {
                      const cleanedAddress = addressData.address.replace(/[^\x20-\x7E]/g, '');
                      const earth911Link = `https://search.earth911.com/?what=${keywordString}&latitude=${latitude}&longitude=${longitude}&max_distance=25`;
                      const sectionTitle = document.createElement('a');
                      sectionTitle.href = earth911Link;
                      sectionTitle.target = "_blank";
                      sectionTitle.className = 'section-title';

                      if (addressData.address === "Not found, Not found") {
                          document.getElementById('map-container').style.display = 'none';
                      } else if (cleanedAddress.startsWith(', ')) {
                          sectionTitle.textContent = 'Mail In Location';
                          displayMap([cleanedAddress], sectionTitle);
                      } else {
                          sectionTitle.textContent = 'Recycling Location';
                          displayMap([cleanedAddress], sectionTitle);
                      }

                      const completeData = {
                          ...data,
                          latitude,
                          longitude,
                          address: cleanedAddress,
                          date: new Date().toISOString()
                      };
                      saveResponseLocally(completeData);
                  })
                  .catch(error => {
                      console.error('Error fetching address:', error);
                      displayError('Error fetching address: ' + error.message);
                      document.getElementById('map-container').style.display = 'none';
                  });
          },
          error => {
              console.error('Geolocation error:', error);
              displayError('Geolocation error: ' + error.message);
              alert('Geolocation error: ' + error.message + ". Please enable location services in your device settings.");
              requestGeolocationPermission();
          }
      );
  } else {
      alert('Geolocation is not supported by this browser.');
      displayError('Geolocation is not supported by this browser.');
  }
}

function requestGeolocationPermission() {
  navigator.geolocation.getCurrentPosition(
      position => {
          console.log('Geolocation granted.');
      },
      error => {
          console.error('Geolocation permission denied.', error);
          displayError('Geolocation permission denied: ' + error.message);
          alert('Geolocation permission is required for this feature. Please enable location services.');
      }
  );
}

function displayError(errorMessage) {
  const existingError = document.getElementById('error-info');
  if (existingError) return; // Prevent multiple error messages
  const errorInfo = document.createElement('div');
  errorInfo.id = 'error-info';
  errorInfo.style.color = 'red';
  errorInfo.style.textAlign = 'center';
  errorInfo.style.margin = '10px';
  errorInfo.innerHTML = errorMessage;
  document.body.appendChild(errorInfo);
}

function displayMap(addresses, sectionTitle) {
  const mapContainer = document.getElementById('map-container');
  mapContainer.innerHTML = ''; 
  mapContainer.appendChild(sectionTitle); 

  addresses.forEach(address => {
      const mapFrame = document.createElement('iframe');
      const mapWrapper = document.createElement('div');
      mapWrapper.className = 'map-frame-wrapper';
      mapFrame.style.width = '100%';
      mapFrame.style.height = '100%';
      mapFrame.style.borderRadius = '24px';
      mapFrame.style.border = 'none';
      mapFrame.loading = 'lazy';
      mapFrame.allowFullscreen = true;
      mapFrame.src = `https://www.google.com/maps/embed/v1/place?key=${googleMapsApiKey}&q=${encodeURIComponent(address)}&maptype=satellite`;
      mapWrapper.appendChild(mapFrame);
      mapContainer.appendChild(mapWrapper);
      mapContainer.style.display = 'block';
  });
}

function formatBoldAndNewLine(text) {
  text = text.replace(/\*\*(.*?)\*\*:/g, '<strong>$1</strong>:<br>');
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/^\*([^\n]*)/gm, '<br>* $1');
  return text;
}

function displayYouTubeVideos(videoData) {
    const videoContainer = document.getElementById('video-container');
    videoContainer.innerHTML = ''; // Clear previous content

    // Extract video ID and aspect ratio from the response
    const videoSuggestion = videoData?.video_suggestion;
    const aspectRatio = videoData?.aspect_ratio || 16 / 9;

    // Log the value and type of videoSuggestion
    console.log("Received video suggestion:", videoSuggestion, "Type:", typeof videoSuggestion);

    // Check for a valid non-empty string
    if (typeof videoSuggestion !== 'string' || videoSuggestion.trim() === '') {
        console.log("No valid video suggestion available:", videoSuggestion);
        videoContainer.style.display = 'none'; // Hide the container if no video is found
        return;
    }

    // Display the section title since there is a valid video suggestion
    const sectionTitle = document.createElement('div');
    sectionTitle.className = 'section-title';
    sectionTitle.textContent = 'Videos';
    videoContainer.appendChild(sectionTitle);

    // Create the iframe container
    const iframeContainer = document.createElement('div');
    iframeContainer.className = 'video-frame-container';

    // Create the iframe element for YouTube video
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${videoSuggestion}`;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    iframe.allowFullscreen = true;

    iframeContainer.appendChild(iframe);
    videoContainer.appendChild(iframeContainer);

    // Dynamically set padding-top based on aspect ratio
    const paddingPercentage = (100 / aspectRatio).toFixed(2);
    iframeContainer.style.paddingTop = `${paddingPercentage}%`;

    // Ensure the container is visible
    videoContainer.style.display = 'block';

    console.log("Displaying video with ID:", videoSuggestion);
}



function fetchAndDisplayProducts(keyword, data) {
    const keywordString = keyword;
    fetch(`/scrape_products?keyword=${keywordString}`)
        .then(response => response.json())
        .then(products => {
            const productContainer = document.getElementById('product-container');
            const cardStack = productContainer.querySelector('.card-stack');

            if (products.length > 0) {
                productContainer.style.display = 'block';

                // Preload images
                preloadImages(products.map(product => product.image_url))
                    .then(() => {
                        // Clear existing cards
                        cardStack.innerHTML = '';

                        // Limit to top 3 products for stacking effect
                        const topProducts = products.slice(0, 3);

                        topProducts.forEach((product, index) => {
                            const card = document.createElement('div');
                            card.classList.add('product-card');
                            if (index === 0) {
                                card.classList.add('active');
                            } else if (index === 1) {
                                card.classList.add('next');
                            } else if (index === 2) {
                                card.classList.add('last');
                            }

                            // Wrap card content in an anchor tag for navigation
                            const cardContent = document.createElement('a');
                            cardContent.href = product.link;
                            cardContent.target = '_blank';
                            cardContent.style.display = 'flex';
                            cardContent.style.flexDirection = 'column';
                            cardContent.style.width = '100%';
                            cardContent.style.height = '100%';
                            cardContent.style.textDecoration = 'none';
                            cardContent.style.color = 'inherit';

                            cardContent.innerHTML = `
                                <img src="${product.image_url}" alt="${product.title}">
                                <div class="labels">
                                    <h3>${product.title}</h3>
                                    <p>${product.price}</p>
                                </div>
                            `;

                            card.appendChild(cardContent);

                            // Add swipe functionality to the active card
                            if (index === 0) {
                                addSwipeListeners(card, products, cardStack);
                            }

                            cardStack.appendChild(card);
                        });

                        // If there are more than 3 products, store the remaining for cycling
                        if (products.length > 3) {
                            cardStack.dataset.cycle = JSON.stringify(products.slice(3));
                        }

                        const completeData = {
                            ...data,
                            products,
                            date: new Date().toISOString()
                        };
                        saveResponseLocally(completeData);
                    })
                    .catch(error => {
                        console.error('Error preloading images:', error);
                        displayError('Some images failed to load, but the products will still be displayed.');
                    });                    
            } else {
                // Hide product container if no products are returned
                productContainer.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching products:', error);
            displayError('Error fetching products: ' + error.message);
            document.getElementById('product-container').style.display = 'none';
        });
}

function preloadImages(imageUrls) {
    const promises = imageUrls.map(url => {
        return new Promise((resolve) => {
            const img = new Image();
            img.src = url;

            img.onload = resolve;
            img.onerror = () => {
                console.warn(`Image failed to load: ${url}`);
                resolve(); // Resolve even if the image fails to load
            };
        });
    });

    return Promise.all(promises);
}

function addSwipeListeners(card, products, cardStack) {
  let startX, startY, currentX, currentY, isDragging = false;
  let startTime;
  const threshold = 100; // Minimum swipe distance

  card.addEventListener('touchstart', touchStart, { passive: true });
  card.addEventListener('touchmove', touchMove, { passive: false });
  card.addEventListener('touchend', touchEnd);

  function touchStart(e) {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      isDragging = true;
      startTime = new Date().getTime();

      // Haptic feedback on touch start
      if (navigator.vibrate) {
          navigator.vibrate(10);
      }
  }

  function touchMove(e) {
      if (!isDragging) return;
      currentX = e.touches[0].clientX - startX;
      currentY = e.touches[0].clientY - startY;

      // Apply rotation based on horizontal movement
      const rotate = currentX / 20;
      card.style.transform = `translate(${currentX}px, ${currentY}px) rotate(${rotate}deg)`;
      card.style.transition = 'none';

      // Visual feedback: scaling
      const scale = Math.max(0.95, 1 - Math.abs(currentX) / window.innerWidth);
      card.style.opacity = scale;

      e.preventDefault(); // Prevent scrolling
  }

  function touchEnd(e) {
      if (!isDragging) return;
      isDragging = false;

      const deltaX = currentX;
      const deltaY = currentY;
      const endTime = new Date().getTime();
      const timeTaken = endTime - startTime;

      // Calculate velocity
      const velocity = Math.sqrt(deltaX * deltaX + deltaY * deltaY) / timeTaken;

      // Determine swipe direction
      if (Math.abs(deltaX) > threshold) {
          // Swipe Left or Right
          const direction = deltaX > 0 ? 'right' : 'left';
          swipeCard(direction, deltaY, velocity);
      } else {
          // Return card to original position
          card.style.transition = 'transform 0.3s ease-out';
          card.style.transform = 'translate(0px, 0px) rotate(0deg)';
          card.style.opacity = '1';
      }
  }

  function swipeCard(direction, deltaY, velocity) {
      // Animate card out of view with velocity
      const exitX = direction === 'right' ? window.innerWidth : -window.innerWidth;
      const exitY = deltaY > 0 ? window.innerHeight : -window.innerHeight;
      const duration = Math.max(300 / velocity, 200); // Adjust duration based on velocity

      card.style.transition = `transform ${duration}ms ease-out`;
      card.style.transform = `translate(${exitX}px, ${exitY}px) rotate(${direction === 'right' ? 45 : -45}deg)`;
      card.style.opacity = '0';

      // Haptic feedback on successful swipe
      if (navigator.vibrate) {
          navigator.vibrate([50, 30, 50]);
      }

      // After animation, move the card to the bottom of the stack
      card.addEventListener('transitionend', () => {
          card.style.transition = 'none';
          card.style.transform = 'translate(0px, 0px) rotate(0deg)';
          card.style.opacity = '1';
          card.classList.remove('active', 'next', 'last');

          // Move the first product to the end
          products.push(products.shift());

          // Re-render the stack
          renderCardStack(products, cardStack);
      }, { once: true });
  }

  function renderCardStack(products, cardStack) {
      // Clear existing cards
      cardStack.innerHTML = '';

      // Render top 3 products
      const topProducts = products.slice(0, 3);
      topProducts.forEach((product, index) => {
          const newCard = document.createElement('div');
          newCard.classList.add('product-card');
          if (index === 0) {
              newCard.classList.add('active');
              addSwipeListeners(newCard, products, cardStack);
          } else if (index === 1) {
              newCard.classList.add('next');
          } else if (index === 2) {
              newCard.classList.add('last');
          }

          // Wrap card content in an anchor tag for navigation
          const cardContent = document.createElement('a');
          cardContent.href = product.link;
          cardContent.target = '_blank';
          cardContent.style.display = 'flex';
          cardContent.style.flexDirection = 'column';
          cardContent.style.width = '100%';
          cardContent.style.height = '100%';
          cardContent.style.textDecoration = 'none';
          cardContent.style.color = 'inherit';

          cardContent.innerHTML = `
              <img src="${product.image_url}" alt="${product.title}">
              <div class="labels">
                  <h3>${product.title}</h3>
                  <p>${product.price}</p>
              </div>
          `;

          newCard.appendChild(cardContent);
          cardStack.appendChild(newCard);
      });
  }
}

window.onload = function() {
  const data = JSON.parse(sessionStorage.getItem('AIResponse'));
  if (!data) {
      displayError('No AI response data found in session storage.');
      return;
  }
  displayEcoPoint();
  const analysisResult = document.getElementById('analysis-result');
  const mapContainer = document.getElementById('map-container');
  const videoContainer = document.getElementById('video-container');

  if (data.result) {
      analysisResult.innerHTML = formatBoldAndNewLine(data.result);
      incrementEcoPoint();
  } else {
      analysisResult.innerHTML = 'Sorry, something went wrong. Please try again.';
  }

  if (data.text_tool === 'J' && data.barcode_image_url) {
      const barcodeImage = document.createElement('img');
      barcodeImage.src = data.barcode_image_url;
      barcodeImage.alt = 'Barcode Image';
      barcodeImage.style.borderRadius = '12px';
      analysisResult.appendChild(barcodeImage);
  }

  saveResponseLocally({
      result: data.result || null,
      date: new Date().toISOString(),
  });

  if (data.text_tool === 'B' && data.keyword) {
      fetchAddressAndDisplay(data.keyword, data);
  }

  if (data.keyword) {
      fetchAndDisplayProducts(data.keyword, data);
  }

  if (data.video_suggestion) {
    displayYouTubeVideos(data); // Pass the entire data object
    videoContainer.style.display = 'block';
    }

  sessionStorage.removeItem('AIResponse');
  requestGeolocationPermission();
};
