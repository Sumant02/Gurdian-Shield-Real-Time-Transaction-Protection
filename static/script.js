
async function checkUserDetails() {
  const cardNumber = document.getElementById('cardNumber').value;
  const cardHolderName = document.getElementById('cardHolderName').value;
  const expiryDate = document.getElementById('expiryDate').value;
  const cvv = document.getElementById('cvv').value;
  const phoneNumber = document.getElementById('phoneNumber').value; // Added phone number
  const location = document.getElementById('location').value; // Added location

  try {
    const response = await fetch('/check-user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        cardNumber, 
        cardHolderName, 
        expiryDate, 
        cvv, 
        phoneNumber,   // Send phone number for lookup
        location       // Send location for lookup
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      document.getElementById('result').innerText = result.message; 
      return true; 
    } else {
      document.getElementById('result').innerText = result.message; 
      return false; 
    }
  } catch (error) {
    console.error('Error checking user details:', error);
    return false; 
  }
}

async function sendOTP() {
  const phoneNumber = document.getElementById('phoneNumber').value;

  try {
    const response = await fetch('/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phoneNumber })  
    });
    const result = await response.json();
    document.getElementById('result').innerText = result.message;
  } catch (error) {
    console.error('Error sending OTP:', error);
  }
}


async function verifyOTP() {
  const phoneNumber = document.getElementById('phoneNumber').value;
  const otp = document.getElementById('otp').value;

  try {
    const response = await fetch('/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phoneNumber, otp })
    });
    const result = await response.json();
    document.getElementById('result').innerText = result.message;
  } catch (error) {
    console.error('Error verifying OTP:', error);
  }
}


document.getElementById('securityForm').addEventListener('submit', async function(event) {
  event.preventDefault(); 

  // Check user details first
  const userDetailsValid = await checkUserDetails(); 

  if (userDetailsValid) {

    let formData = new FormData(this);
    
    try {
      const response = await fetch('/predict', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      document.getElementById('result').innerHTML = `Transaction Status: ${data.result}`;
    } catch (error) {
      console.error('Error:', error);
    }
  }
});