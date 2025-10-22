# SmartShelf - Inventory Management System

A modern inventory management system built with FastAPI backend and React frontend.

## Features

- 📊 **Dashboard** - Overview of inventory statistics and recent alerts
- 📦 **Inventory Management** - Track stock levels, thresholds, and safety stock
- 🏷️ **Items Management** - Manage product catalog with SKU, categories, and units
- 🛒 **Orders Management** - Handle customer orders and fulfillment
- ⚠️ **Alerts System** - Monitor low stock and system alerts
- 🔄 **Restocks Management** - Track restock requests and fulfillment

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **APScheduler** - Background job scheduling

### Frontend
- **React 19** - Modern React with hooks
- **Material-UI (MUI)** - Beautiful UI components
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Recharts** - Data visualization

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (for PostgreSQL)

### Backend Setup

1. **Start the database:**
   ```bash
   cd SmartShelf/backend
   docker-compose up -d
   ```

2. **Install dependencies:**
   ```bash
   cd SmartShelf/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the backend server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   Backend will be available at: http://localhost:8000
   API Documentation: http://localhost:8000/docs

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd SmartShelf/frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

   Frontend will be available at: http://localhost:3000

## API Endpoints

- `GET /api/v1/items` - List all items
- `POST /api/v1/items` - Create new item
- `GET /api/v1/inventory` - List inventory
- `PUT /api/v1/inventory/{id}` - Update inventory
- `GET /api/v1/orders` - List orders
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/restocks` - List restocks

## Database Schema

The system includes the following main entities:
- **Items** - Product catalog
- **Areas** - Storage locations
- **Inventory** - Stock levels per item/area
- **Orders** - Customer orders
- **Alerts** - System notifications
- **Restocks** - Restock requests

## Development

### Backend Development
- The backend uses async/await patterns
- Database models are defined in `app/db/models.py`
- API routes are in `app/api/v1/`
- Background jobs are in `app/workers/tasks.py`

### Frontend Development
- Components are organized in `src/components/`
- Pages are in `src/pages/`
- API service is in `src/services/api.js`
- Uses Material-UI for consistent styling

## Production Deployment

1. **Backend:**
   - Use a production ASGI server like Gunicorn
   - Set up proper environment variables
   - Configure database connection pooling

2. **Frontend:**
   - Build the production bundle: `npm run build`
   - Serve static files with a web server like Nginx

## License

This project is for educational purposes.