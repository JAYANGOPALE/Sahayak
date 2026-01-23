const express = require('express');
const router = express.Router();
const User = require('../models/User');

// @route   POST /api/customer/register
// @desc    Register a customer and send OTP
router.post('/register', async (req, res) => {
  const { mobileNumber } = req.body;

  try {
    let user = await User.findOne({ mobileNumber });

    if (!user) {
      user = new User({
        mobileNumber,
        userType: 'customer',
      });
    }

    // Generate a 4-digit OTP
    const otp = Math.floor(1000 + Math.random() * 9000).toString();
    user.otp = otp;
    user.otpExpires = Date.now() + 10 * 60 * 1000; // 10 minutes

    await user.save();

    // In a real app, you would send the OTP via SMS
    res.json({ msg: 'OTP sent successfully', otp });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route   POST /api/customer/login
// @desc    Login a customer with OTP
router.post('/login', async (req, res) => {
  const { mobileNumber, otp } = req.body;

  try {
    const user = await User.findOne({ mobileNumber });

    if (!user) {
      return res.status(400).json({ msg: 'User not found' });
    }

    if (user.otp !== otp || user.otpExpires < Date.now()) {
      return res.status(400).json({ msg: 'Invalid or expired OTP' });
    }

    // In a real app, you would generate a JWT token here
    res.json({ msg: 'Login successful' });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

module.exports = router;
