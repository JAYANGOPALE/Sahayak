const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  name: {
    type: String,
  },
  mobileNumber: {
    type: String,
    required: true,
    unique: true,
  },
  email: {
    type: String,
  },
  userType: {
    type: String,
    enum: ['customer', 'partner'],
    required: true,
  },
  otp: {
    type: String,
  },
  otpExpires: {
    type: Date,
  },
});

module.exports = mongoose.model('User', UserSchema);
