# UmugandaTech Backend - Frontend Integration Guide

## 🚀 Quick Start

### Base URL

### API Overview Endpoint

## 🔐 Authentication Flow

### 1. User Registration
```javascript
// Step 1: Register user
const registerResponse = await fetch('http://localhost:8000/api/users/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone_number: '+250123456789'
  })
});
const { otp } = await registerResponse.json(); // OTP returned for development


// Step 2: Verify OTP and set password
const verifyResponse = await fetch('http://localhost:8000/api/users/auth/verify-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone_number: '+250123456789',
    otp: '123456',
    password: 'securepassword',
    first_name: 'John',
    last_name: 'Doe'
  })
});
const { access, refresh, user } = await verifyResponse.json();


// Step 3: Login existing user
const loginResponse = await fetch('http://localhost:8000/api/users/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone_number: '+250123456789',
    password: 'securepassword'
  })
});
const { access, refresh, user } = await loginResponse.json();
//4. Using JWT Tokens
// Include token in all authenticated requests
const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};

//📋 Core API Endpoints
//Projects
//List Projects with Search & Filter

// Get all projects
const projects = await fetch('http://localhost:8000/api/projects/projects/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Search projects
const searchResults = await fetch('http://localhost:8000/api/projects/projects/?search=tree planting', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Filter projects
const filteredProjects = await fetch('http://localhost:8000/api/projects/projects/?status=ongoing&location=kigali', {
  headers: { 'Authorization': `Bearer ${token}` }
});

//Create Project
const newProject = await fetch('http://localhost:8000/api/projects/projects/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Tree Planting Initiative',
    description: 'Community tree planting project',
    sector: 'Kigali',
    datetime: '2024-01-15T09:00:00Z',
    location: 'Nyamirambo',
    required_volunteers: 50,
    status: 'planned'
  })
});


//QR Code & Attendance
//Generate QR Code (Leaders only)
const qrCode = await fetch(`http://localhost:8000/api/projects/projects/${projectId}/generate_qr_code/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
const { qr_code } = await qrCode.json();


//Check-in to Project
const checkin = await fetch('http://localhost:8000/api/projects/checkin/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    qr_code: 'umuganda_checkin:1:abc123'
  })
});

//Check-out from Project
const checkout = await fetch('http://localhost:8000/api/projects/checkout/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    qr_code: 'umuganda_checkin:1:abc123'
  })
});


//Community Features
//Get Posts
const posts = await fetch('http://localhost:8000/api/community/posts/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Create Post
const newPost = await fetch('http://localhost:8000/api/community/posts/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: 'Great project idea!',
    type: 'suggestion',
    project: 1
  })
});

//Upvote Post
const upvote = await fetch(`http://localhost:8000/api/community/posts/${postId}/upvote/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

// Certificates
// Generate Certificate
const certificate = await fetch(`http://localhost:8000/api/projects/certificates/generate/${projectId}/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

// 📊 Data Models
// User Object
{
  "id": 1,
  "phone_number": "+250123456789",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "sector": "Kigali",
  "role": "volunteer",
  "avatar": "http://localhost:8000/media/avatars/user1.jpg",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}

// Project Object
{
  "id": 1,
  "title": "Tree Planting Initiative",
  "description": "Community tree planting project",
  "sector": "Kigali",
  "datetime": "2024-01-15T09:00:00Z",
  "location": "Nyamirambo",
  "required_volunteers": 50,
  "image_url": "http://localhost:8000/media/project/tree.jpg",
  "admin": 1,
  "admin_name": "John Doe",
  "status": "ongoing",
  "created_at": "2024-01-01T00:00:00Z",
  "volunteer_count": 25,
  "is_user_registered": true,
  "skills": []
}

// 🔧 File Uploads
// Upload Project Image

const formData = new FormData();
formData.append('image', file);

const upload = await fetch(`http://localhost:8000/api/projects/projects/${projectId}/upload-image/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

// Upload User Avatar

const formData = new FormData();
formData.append('avatar', file);

const upload = await fetch('http://localhost:8000/api/users/upload-avatar/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

// 🚨 Error Handling
// Common Error Responses

// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

// 400 Bad Request
{
  "phone_number": ["This field is required."]
}

// 404 Not Found
{
  "detail": "Not found."
}

// Error Handling Example
try {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('API Error:', error.message);
  // Handle error in UI
}

// Real-time Features
// Notifications
// Get user notifications
const notifications = await fetch('http://localhost:8000/api/notifications/notifications/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Mark notification as read
const markRead = await fetch(`http://localhost:8000/api/notifications/notifications/${notificationId}/mark_as_read/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
