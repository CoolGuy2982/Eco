const isMobileDevice = () => {
  return /Mobi|Android|iPhone|iPad|iPod/.test(navigator.userAgent);
};

const initialize = () => {
  if (!isMobileDevice()) {
      window.location.href = 'https://www.firley.org/products/ecolens-redirect';
  }    
};