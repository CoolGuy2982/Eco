document.addEventListener("DOMContentLoaded", function(event) {
  setTimeout(function() {
      window.location.href = "/home"; // Redirect to Flask endpoint after a delay
  }, 750); // Delay of 3 seconds
});


<script src="https://apis.google.com/js/platform.js" async defer></script>
  
  function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    var email = profile.getEmail();
    var idToken = googleUser.getAuthResponse().id_token;

    // Send the ID token to the backend for verification and to create a session
    fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ idToken: idToken })
    }).then(response => response.json())
      .then(data => {
        if (data.success) {
          localStorage.setItem('email', email);
          window.location.href = '/home';
        } else {
          console.error('Login failed');
        }
      });
  }
