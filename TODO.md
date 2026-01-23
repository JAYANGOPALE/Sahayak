# Sahayak Project TODO List

## Phase 1: Project Scaffolding & Backend MVP

- [ ] Create project directory structure (`backend`, `customer_app`, `partner_app`).
- [ ] Initialize Node.js project for the backend, and set up Express.js and Socket.IO.
- [ ] Connect to MongoDB database.
- [ ] Define User (Customer, Partner) and Job schemas.
- [ ] Implement API endpoints for user authentication (registration for customers, login for both).
- [ ] Implement WebSocket logic for real-time communication.

## Phase 2: Customer App MVP (React Native with Expo)

- [ ] Initialize an Expo project for the customer app.
- [ ] Create the login/registration screen with mobile number input.
- [ ] Implement the OTP verification screen.
- [ ] Build the home screen dashboard with service selection cards.
- [ ] Create the booking flow UI, including the "searching for helpers" screen.
- [ ] Connect the app to the backend for authentication and real-time updates.

## Phase 3: Partner App MVP (React Native with Expo)

- [ ] Initialize an Expo project for the partner app.
- [ ] Create the simple login screen (mobile number only).
- [ ] Implement the main "On Duty" / "Off Duty" toggle screen.
- [ ] Implement the real-time job request notification screen.
- [ ] Connect the app to the backend to receive live job alerts.

## Phase 4: Integration & Advanced Features

- [ ] Implement the job matching logic on the backend.
- [ ] Implement the full booking and acceptance flow between the two apps.
- [ ] Build the "Security Handshake" feature (Start PIN and Selfie verification).
- [ ] Integrate a payment solution.
- [ ] Implement the rating and review system for both users and partners.
- [ ] Conduct end-to-end testing of the live data flow.
