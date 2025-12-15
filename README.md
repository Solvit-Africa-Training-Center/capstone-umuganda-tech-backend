# Umuganda Community Platform - Backend API

A comprehensive Django REST API backend for managing Rwanda's Umuganda community service platform, enabling citizens to participate in monthly community work projects, track attendance, and generate impact reports.

## Problem Statement

Rwanda's monthly Umuganda community service requires better coordination and tracking systems. Traditional paper-based attendance and manual project management create inefficiencies, lack of transparency, and difficulty in measuring community impact. This platform digitizes the entire process, from project creation to attendance tracking and certificate generation.

## Features

### Core Features
- **User Management**: Multi-role authentication (Admin, Leader, Volunteer) with JWT tokens
- **Project Management**: Create, update, and manage community projects with categories and skills
- **QR Code Check-in**: Automated attendance tracking using generated QR codes
- **Real-time Notifications**: SMS integration via Twilio for project updates
- **Certificate Generation**: Automated PDF certificate creation for participants
- **Dashboard Analytics**: Project statistics, volunteer metrics, and impact tracking

### Advanced Features
- **Leader Following System**: Users can follow project leaders for updates
- **Project Registration**: Pre-registration system with capacity management
- **Impact Metrics**: Track and measure community project outcomes
- **File Management**: Image uploads for projects and user profiles
- **Advanced Filtering**: Search projects by location, sector, status, and skills
- **API Documentation**: Interactive Swagger/OpenAPI documentation

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | Django 5.2.5 + Django REST Framework 3.16.1 |
| **Database** | PostgreSQL 15 |
| **Authentication** | JWT (Simple JWT) |
| **File Storage** | Django File Storage + WhiteNoise |
| **SMS Service** | Twilio API |
| **Documentation** | drf-yasg (Swagger/OpenAPI) |
| **Containerization** | Docker + Docker Compose |
| **Deployment** | Render.com (Production) |

## Architecture & Project Structure
