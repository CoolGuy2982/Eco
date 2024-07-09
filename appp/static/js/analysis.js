function fetchAddressAndDisplay(keyword, data) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(position => {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;
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
          document.getElementById('map-container').style.display = 'none'; // Hide map on error
        });
    }, () => {
      alert('Unable to retrieve your location');
    });
  } else {
    alert('Geolocation is not supported by this browser.');
  }
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
      document.getElementById('product-container').style.display = 'none'; // Hide on error
    });
}

function setupCarousel() {
  const carousel = document.querySelector('.carousel');
  const nextButton = document.createElement('button');
  nextButton.textContent = '>';
  nextButton.classList.add('next');
  nextButton.onclick = () => {
    carousel.scrollBy({left: 300, behavior: 'smooth'});
  };

  const prevButton = document.createElement('button');
  prevButton.textContent = '<';
  prevButton.classList.add('prev');
  prevButton.onclick = () => {
    carousel.scrollBy({left: -300, behavior: 'smooth'});
  };

  carousel.before(prevButton);
  carousel.after(nextButton);
}

function saveResponseLocally(data) {
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
}

function mergeResponses(responses) {
  const mergedResponses = [];

  responses.forEach(response => {
    const lastResponse = mergedResponses[mergedResponses.length - 1];

    if (lastResponse && (new Date(response.date) - new Date(lastResponse.date)) <= 30000) {
      // Merge if within 30 seconds
      lastResponse.result = lastResponse.result || response.result;
      lastResponse.keyword = lastResponse.keyword || response.keyword;
      lastResponse.latitude = lastResponse.latitude || response.latitude;
      lastResponse.longitude = lastResponse.longitude || response.longitude;
      lastResponse.video_suggestion = lastResponse.video_suggestion || response.video_suggestion;
      lastResponse.product_option_chosen = lastResponse.product_option_chosen || response.product_option_chosen;

      if (response.products) {
        lastResponse.products = lastResponse.products || [];
        response.products.forEach(product => {
          if (!lastResponse.products.some(p => p.title === product.title && p.price === product.price)) {
            lastResponse.products.push(product);
          }
        });
      }
    } else {
      mergedResponses.push(response);
    }
  });

  return mergedResponses;
}

function showEcoPoint() {
  let ecoPoints = localStorage.getItem('ecoPoints') ? parseInt(localStorage.getItem('ecoPoints')) : 0;
  ecoPoints += 1;
  localStorage.setItem('ecoPoints', ecoPoints);

  const ecoPoint = document.getElementById('eco-point');
  ecoPoint.classList.add('visible');

  setTimeout(() => {
    ecoPoint.classList.remove('visible');
  }, 3000);
}

window.onload = function() {
  const data = JSON.parse(sessionStorage.getItem('AIResponse'));
  if (!data) {
    console.error('No AI response data found in session storage.');
    return;
  }

  const analysisResult = document.getElementById('analysis-result');
  const ecoPoint = document.getElementById('eco-point');
  const mapContainer = document.getElementById('map-container');
  const videoContainer = document.getElementById('video-container');

  if (data.result) {
    analysisResult.innerHTML = formatBoldAndNewLine(data.result);
    showEcoPoint();
  } else {
    analysisResult.innerHTML = 'Sorry bout dat, we prolly messed something up. Please try again';
  }

  // Save initial response data
  const initialData = {
    result: data.result || null,
    video_suggestion: data.video_suggestion || null,
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
};
