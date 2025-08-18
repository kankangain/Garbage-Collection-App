# Garbage Collection Request System

A comprehensive web application for managing garbage collection requests in municipal areas. Built with Django, this system enables citizens to report garbage collection needs while providing administrative tools for efficient waste management.

## 🌟 Features

### For Citizens (Users)
- **Account Creation**: Sign up using phone number (email optional)
- **Request Submission**: Submit garbage collection requests with:
  - Personal details (name, address, phone, email)
  - Location details (ward number, landmark)
  - Garbage category selection
  - Photo capture/upload (mobile-optimized)
  - Optional description
- **Request Tracking**: Monitor request status in real-time
- **Request History**: View all past requests and their outcomes
- **Profile Management**: Update personal information
- **Notifications**: Receive updates on request progress

### For Labour Workers
- **Task Dashboard**: View assigned garbage collection tasks
- **Work Management**: 
  - Start work on assigned tasks
  - Upload completion photos
  - Add completion notes
- **Time Tracking**: Monitor 72-hour completion deadline
- **Status Updates**: Update work progress in real-time

### For Councilors
- **Ward Management**: Manage requests within assigned ward
- **Labour Assignment**: Assign requests to available labour workers
- **Report Review**: 
  - Approve/reject completion reports
  - Provide feedback on rejected reports
- **Ward Statistics**: View ward-specific analytics
- **Notification Management**: Receive alerts for new requests and overdue tasks

### For Chairman
- **System Overview**: View all requests across all wards
- **Analytics Dashboard**: Comprehensive statistics and reporting
- **Ward Filtering**: Sort and filter requests by ward numbers
- **Overdue Monitoring**: Track requests exceeding 72-hour deadline
- **System Administration**: Manage users and overall system health

## 🏗️ System Architecture

### User Roles
1. **Chairman**: Full system access, analytics, overdue monitoring
2. **Councilor**: Ward-specific management, labour assignment, report approval
3. **Labour**: Task execution, completion reporting
4. **User**: Request submission, tracking, profile management

### Core Workflow
1. **Request Creation**: User submits garbage collection request
2. **Assignment**: Councilor assigns request to labour worker
3. **Execution**: Labour worker completes task within 72 hours
4. **Reporting**: Labour uploads completion photo
5. **Approval**: Councilor approves/rejects completion report
6. **Completion**: Request marked as completed

### Key Features
- **72-Hour Deadline**: Automatic alerts for overdue requests
- **Image Management**: Photo capture and upload functionality
- **Real-time Notifications**: Push notifications for all stakeholders
- **Ward-based Organization**: Requests organized by 20 ward system
- **Mobile-First Design**: Optimized for mobile devices and future Android app
- **Role-based Access Control**: Secure access based on user roles

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2+
- Pillow (for image handling)

### Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd garbage-collection-system
   pip install -r requirements.txt
   ```

2. **Database Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access Application**
   - Web App: `http://localhost:8000`
   - Admin Panel: `http://localhost:8000/admin`

### Production Deployment
For production deployment, ensure:
- Use PostgreSQL/MySQL instead of SQLite
- Configure proper media file serving
- Set up proper static file handling
- Configure environment variables
- Set DEBUG=False

## 📱 Mobile Integration

This web application is designed with mobile-first principles and can be easily integrated into an Android app using Koduler or similar WebView-based solutions:

### WebView Integration Features
- Responsive design for all screen sizes
- Camera integration for photo capture
- Touch-optimized interface
- Offline capability considerations
- Push notification ready

### Android App Integration
The system is built to support future Android app integration with:
- RESTful API endpoints
- JSON response formats
- Token-based authentication
- Push notification infrastructure

## 🛠️ Technology Stack

- **Backend**: Django 5.2, Python
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Image Processing**: Pillow
- **Icons**: Bootstrap Icons
- **Mobile Support**: Progressive Web App ready

## 📊 Database Schema

### Core Models
- **CustomUser**: Extended user model with role and ward information
- **Profile**: User profile with personal details
- **GarbageRequest**: Main request entity with location and category
- **CompletionReport**: Labour completion reports with images
- **RequestTracking**: Activity timeline for requests
- **Notification**: Push notification system
- **DeviceToken**: Mobile device registration for notifications

## 🔧 Configuration

### Settings Configuration
Key settings in `settings.py`:
- `AUTH_USER_MODEL`: Custom user model
- `MEDIA_URL` and `MEDIA_ROOT`: File upload configuration
- Ward system configuration (1-20 wards)
- Notification system settings

### User Roles Configuration
The system supports four user roles:
- `chairman`: Full system access
- `councilor`: Ward-specific management
- `labour`: Task execution
- `user`: Request submission

## 🎯 Key Features Detail

### Request Management
- **Category System**: Support for various garbage types
- **Ward System**: 20-ward organizational structure
- **Status Tracking**: Complete lifecycle monitoring
- **Image Documentation**: Before/after photo requirements

### Notification System
- **Real-time Updates**: Instant notifications for status changes
- **Role-based Notifications**: Targeted messages based on user role
- **Push Notification Ready**: Infrastructure for mobile push notifications
- **Email Integration**: Optional email notifications

### Analytics & Reporting
- **Dashboard Analytics**: Real-time statistics
- **Ward-wise Reports**: Location-based analytics
- **Performance Metrics**: Completion rates and response times
- **Export Capabilities**: Data export functionality

## 🔒 Security Features

- **Role-based Access Control**: Secure access management
- **CSRF Protection**: Built-in Django security
- **File Upload Security**: Safe image upload handling
- **Authentication**: Secure login system
- **Data Validation**: Form and data validation

## 📈 Future Enhancements

- **GPS Integration**: Automatic location detection
- **Map Integration**: Visual request mapping
- **Advanced Analytics**: Machine learning insights
- **Multi-language Support**: Localization
- **API Enhancement**: Full REST API
- **Mobile App**: Native Android/iOS applications

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation

## 🏆 Acknowledgments

- Bootstrap team for the excellent CSS framework
- Django community for the robust web framework
- All contributors and testers

---

**Making our city cleaner, one request at a time.** 🌱
