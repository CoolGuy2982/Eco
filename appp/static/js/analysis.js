function saveResponseLocally(data) {
  try {
    let pastResponses = JSON.parse(localStorage.getItem('pastResponses')) || [];
    console.log('Initial pastResponses:', pastResponses); // Debugging log
    const existingIndex = pastResponses.findIndex(response => response.date === data.date);

    if (existingIndex > -1) {
      // Merge the new data with the existing data
      pastResponses[existingIndex] = { ...pastResponses[existingIndex], ...data };
    } else {
      pastResponses.push(data);
    }

    try {
      localStorage.setItem('pastResponses', JSON.stringify(pastResponses));
      console.log('Past responses updated:', pastResponses);
      //displayPastResponses(); // Display past responses for testing
    } catch (error) {
      if (error.code === 22) {
        // QuotaExceededError
        console.warn('Quota exceeded, removing oldest entries');
        while (error.code === 22 && pastResponses.length > 0) {
          pastResponses.shift(); // Remove the oldest entry
          try {
            localStorage.setItem('pastResponses', JSON.stringify(pastResponses));
            error = null;
            console.log('Past responses updated after removing oldest entry:', pastResponses);
          } catch (e) {
            error = e;
            console.warn('Still exceeding quota, removing more entries');
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
  ecoPointElement.textContent = `+1 EcoPoint`;
  ecoPointElement.classList.add('visible');

  setTimeout(() => {
    ecoPointElement.classList.remove('visible');
  }, 3000); // Hide after 3 seconds
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
            console.log('Scraped Address:', addressData.address);
            const cleanedAddress = addressData.address.replace(/[^\x20-\x7E]/g, '');
            const earth911Link = `https://search.earth911.com/?what=${keywordString}&latitude=${latitude}&longitude=${longitude}&max_distance=25`;
            const sectionTitle = document.createElement('a');
            sectionTitle.href = earth911Link;
            sectionTitle.target = "_blank";
            sectionTitle.className = 'section-title';

            if (addressData.address === "Not found, Not found") {
              console.log('Address not valid:', cleanedAddress);
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
            console.log('Saving complete analysis data:', completeData);
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
  // Convert **bold**: to <strong>bold</strong>:<br>
  text = text.replace(/\*\*(.*?)\*\*:/g, '<strong>$1</strong>:<br>');
  
  // Convert **bold** to <strong>bold</strong>
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert lines starting with * to <br>* for bullet points
  text = text.replace(/^\*([^\n]*)/gm, '<br>* $1');
  
  // Ensure that bullet points are separated properly
  text = text.replace(/^\*([^\n]*)/gm, '<br>* $1');
  
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
  const keywordString = keyword;
  fetch(`/scrape_products?keyword=${keywordString}`)
    .then(response => response.json())
    .then(products => {
      if (products.length > 0) {
        let currentIndex = 0;

        const productContainer = document.getElementById('product-container');
        productContainer.style.display = 'block';
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
      document.getElementById('product-container').style.display = 'none';
    });
}

window.onload = function() {
  // displayPastResponses(); // Display past responses on load for testing
  const data = JSON.parse(sessionStorage.getItem('AIResponse'));
  if (!data) {
    console.error('No AI response data found in session storage.');
    displayError('No AI response data found in session storage.');
    return;
  }
  displayEcoPoint();
  const analysisResult = document.getElementById('analysis-result');
  const mapContainer = document.getElementById('map-container');
  const videoContainer = document.getElementById('video-container');

  if (data.result) {
    analysisResult.innerHTML = formatBoldAndNewLine(data.result);
    incrementEcoPoint(); // Increment EcoPoint on valid AI response
  } else {
    analysisResult.innerHTML = 'Sorry bout dat, I prolly messed something up. pls try again :)';
  }

  // Display barcode image if the text_tool is 'J' and barcode_image_url is present
  if (data.text_tool === 'J' && data.barcode_image_url) {
    const barcodeImage = document.createElement('img');
    barcodeImage.src = data.barcode_image_url;
    barcodeImage.alt = 'Barcode Image';
    barcodeImage.style.borderRadius = '12px';
    barcodeImage.style.display = 'block';
    barcodeImage.style.marginTop = '20px';
    barcodeImage.style.width = '100%';
    barcodeImage.style.maxWidth = '400px'; // Limit the width for better display
    barcodeImage.style.marginLeft = 'auto';
    barcodeImage.style.marginRight = 'auto';

    analysisResult.appendChild(barcodeImage);
  }

  // Save initial response data
  const initialData = {
    result: data.result || null,
    video_suggestion: data.video_suggestion || null,
    date: new Date().toISOString(),
    barcode_image_url: data.barcode_image_url || null
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
