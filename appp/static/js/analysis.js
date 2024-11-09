// javascript code to process image the received analysis for analysis page 
function saveResponseLocally(data) {
  try {
    let pastResponses = JSON.parse(localStorage.getItem('pastResponses')) || [];
    console.log('Initial pastResponses:', pastResponses);
    const existingIndex = pastResponses.findIndex(response => response.date === data.date);

    if (existingIndex > -1) {
      pastResponses[existingIndex] = { ...pastResponses[existingIndex], ...data };
    } else {
      pastResponses.push(data);
    }

    try {
      localStorage.setItem('pastResponses', JSON.stringify(pastResponses));
      console.log('Past responses updated:', pastResponses);
    } catch (error) {
      if (error.code === 22) {
        console.warn('Quota exceeded, removing oldest entries');
        while (error.code === 22 && pastResponses.length > 0) {
          pastResponses.shift(); 
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
