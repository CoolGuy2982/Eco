// javascript code for the browse page
const isMobileDevice = () => {
  return /Mobi|Android|iPhone|iPad|iPod/.test(navigator.userAgent);
};

const initialize = () => {
  if (!isMobileDevice()) {
      window.location.href = 'https://www.firley.net/products/ecolens-redirect';
  }    
};

initialize();