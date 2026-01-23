const BASE_URL = 'http://localhost:3000/api';

export const sendOtp = async (mobileNumber) => {
  try {
    const response = await fetch(`${BASE_URL}/customer/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mobileNumber }),
    });
    return response.json();
  } catch (error) {
    console.error('Error sending OTP:', error);
    throw error;
  }
};

export const verifyOtp = async (mobileNumber, otp) => {
  try {
    const response = await fetch(`${BASE_URL}/customer/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mobileNumber, otp }),
    });
    return response.json();
  } catch (error) {
    console.error('Error verifying OTP:', error);
    throw error;
  }
};
