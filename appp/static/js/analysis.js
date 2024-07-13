function fetchAddressAndDisplay(keyword, data) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      position => {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        displayLocationInfo(latitude, longitude);
        const keywordString = encodeURIComponent(keyword); // Ensure keyword is URL encoded
        const url = `/scrape_address?what=${keywordString}&latitude=${latitude}&longitude=${longitude}`;

        fetch(url)
          .then(response => response.json())
          .then(addressData => {
            console.log('Scraped Address:', addressData.address);
            const cleanedAddress = addressData.address.replace(/[^\x20-\x7E]/g, '');
            const earth911Link = `https://search.earth911.com/?what=${keywordString}&latitude=${latitude}&longitude=${longitude}&max_distance=25`;
            const sectionTitle = document.createElement('a');
            sectionTitle.href = earth911Link;
            sectionTitle.target = "_blank";
            sectionTitle.className = 'section-title';

            if (addressData.address === "Not found, Not found") {
              console.log('Address not valid:', cleanedAddress);
              document.getElementById('map-container').style.display = 'none'; // Hide the map container if address is not valid
            } else if (cleanedAddress.startsWith(', ')) {
              sectionTitle.textContent = 'Mail In Location';
              displayMap([cleanedAddress], sectionTitle);
            } else {
              sectionTitle.textContent = 'Recycling Location';
              displayMap([cleanedAddress], sectionTitle);
            }

            // Update and save the response data with address
            const completeData = {
              ...data,
              latitude,
              longitude,
              address: cleanedAddress,
              date: new Date().toISOString()
            };
            console.log('Saving complete analysis data:', completeData);
            saveResponseLocally(completeData);
          })
          .catch(error => {
            console.error('Error fetching address:', error);
            displayError('Error fetching address: ' + error.message);
            document.getElementById('map-container').style.display = 'none'; // Hide map on error
          });
      },
      error => {
        console.error('Geolocation error:', error);
        displayError('Geolocation error: ' + error.message);
        alert('Geolocation error: ' + error.message + ". Please enable location services in your device settings.");
        // Prompt again for geolocation
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

function displayLocationInfo(latitude, longitude) {
  const locationInfo = document.createElement('div');
  locationInfo.id = 'location-info';
  locationInfo.innerHTML = `Latitude: ${latitude}, Longitude: ${longitude}`;
  document.body.appendChild(locationInfo);
}

function displayError(errorMessage) {
  const errorInfo = document.createElement('div');
  errorInfo.id = 'error-info';
  errorInfo.style.color = 'red';
  errorInfo.innerHTML = errorMessage;
  document.body.appendChild(errorInfo);
}

function displayMap(addresses, sectionTitle) {
  const mapContainer = document.getElementById('map-container');
  mapContainer.innerHTML = ''; // Clear previous content
  mapContainer.appendChild(sectionTitle); // Add the title

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
    mapContainer.style.display = 'block'; // Ensure the map container is visible
  });
}

function formatBoldAndNewLine(text) {
  text = text.replace(/\*\*(.*?)\*\*:/g, '<strong>$1</strong>:<br>');
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/ -([^\n]*)/g, '<br> -$1');
  text = text.replace(/\*([^\n]*)/g, '<br>*$1');
  return text;
}

function displayYouTubeVideos(videoIDs) {
  const videoContainer = document.getElementById('video-container');
  videoContainer.innerHTML = '<div class="section-title">Videos</div>';
  videoIDs.forEach(id => {
    const iframeContainer = document.createElement('div');
    iframeContainer.className = 'video-frame-container';
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${id}`;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    iframe.allowFullscreen = true;
    iframeContainer.appendChild(iframe);
    videoContainer.appendChild(iframeContainer);
  });
}

function fetchAndDisplayProducts(keyword, data) {
  const keywordString = keyword; // Handle multi-word keywords
  fetch(`/scrape_products?keyword=${keywordString}`)
    .then(response => response.json())
    .then(products => {
      if (products.length > 0) {
        let currentIndex = 0;

        const productContainer = document.getElementById('product-container');
        productContainer.style.display = 'block';  // Show the container once products are loaded
        const productCard = productContainer.querySelector('.product-card');

        updateProductDisplay(products, currentIndex);

        window.showNextProduct = function() {
          currentIndex = (currentIndex + 1) % products.length;
          updateProductDisplay(products, currentIndex);
        };

        window.showPreviousProduct = function() {
          currentIndex = (currentIndex - 1 + products.length) % products.length;
          updateProductDisplay(products, currentIndex);
        };

        function updateProductDisplay(products, index) {
          const product = products[index];
          const productElement = productCard.querySelector('.product');
          productElement.querySelector('a').href = product.link;
          productElement.querySelector('img').src = product.image_url;
          productElement.querySelector('img').alt = product.title;
          productElement.querySelector('h3').textContent = product.title;
          productElement.querySelector('p').textContent = product.price;
        }

        // Update and save the response data with products
        const completeData = {
          ...data,
          products,
          date: new Date().toISOString()
        };
        console.log('Saving complete analysis data with products:', completeData);
        saveResponseLocally(completeData);
      }
    })
    .catch(error => {
      console.error('Error fetching products:', error);
      displayError('Error fetching products: ' + error.message);
      document.getElementById('product-container').style.display = 'none'; // Hide on error
    });
}

function saveResponseLocally(data) {
  try {
    const pastResponses = JSON.parse(localStorage.getItem('pastResponses')) || [];
    const existingIndex = pastResponses.findIndex(response => response.date === data.date);

    if (existingIndex > -1) {
      // Merge the new data with the existing data
      pastResponses[existingIndex] = { ...pastResponses[existingIndex], ...data };
    } else {
      pastResponses.push(data);
    }

    localStorage.setItem('pastResponses', JSON.stringify(pastResponses));
    console.log('Past responses updated:', pastResponses);
  } catch (error) {
    console.error('Error saving response locally:', error);
    displayError('Error saving response locally: ' + error.message);
  }
}

window.onload = function() {
  const data = JSON.parse(sessionStorage.getItem('AIResponse'));
  if (!data) {
    console.error('No AI response data found in session storage.');
    displayError('No AI response data found in session storage.');
    return;
  }

  const analysisResult = document.getElementById('analysis-result');
  const ecoPoint = document.getElementById('eco-point');
  const mapContainer = document.getElementById('map-container');
  const videoContainer = document.getElementById('video-container');

  if (data.result) {
    analysisResult.innerHTML = formatBoldAndNewLine(data.result);
  } else {
    analysisResult.innerHTML = 'Sorry bout dat, we prolly messed something up. Please try again';
  }

  // Save initial response data
  const initialData = {
    result: data.result || null,
    video_suggestion: data.video_suggestion || null,
    b64_image: data.image_data,
    date: new Date().toISOString()
  };
  saveResponseLocally(initialData);

  // Check for recycling option and keyword before fetching address
  if (data.text_tool === 'B' && data.keyword) {
    fetchAddressAndDisplay(data.keyword, data); // Fetch and display addresses only if "Recycling"
  } else {
    mapContainer.style.display = 'none'; // Hide the map container if not "Recycling"
  }

  if (data.keyword) {
    fetchAndDisplayProducts(data.keyword, data); // Fetch and display products based on the keyword
  }

  if (data.video_suggestion) {
    displayYouTubeVideos([data.video_suggestion]);
    videoContainer.style.display = 'block';
  } else {
    videoContainer.style.display = 'none';
  }

  sessionStorage.removeItem('AIResponse'); // Clean up after displaying

  // Request geolocation permission on page load
  requestGeolocationPermission();
};
