# Travel Agent AI - Frontend

A React + TypeScript single-page application for the Travel Agent AI system. This frontend connects to a FastAPI backend to generate personalized travel itineraries with destinations, points of interest, events, and weather forecasts.

## 🚀 Features

- **Customer Profile Form**: Collects travel preferences including interests, budget, dates, party size, and departure city
- **AI-Powered Itinerary Generation**: Submits profile to backend and receives curated destination recommendations
- **Rich Destination Cards**: Displays detailed information about each destination including:
  - Rationale for selection
  - Points of interest with categories and visit durations
  - Local events during travel dates
  - Weather forecasts with clothing suggestions
- **Responsive Design**: Works seamlessly on desktop and tablet devices
- **State Management**: Clean state-based UI flow (idle → loading → success/error)
- **Accessible**: Proper ARIA labels, keyboard navigation, and screen reader support

## 🛠️ Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **CSS Modules** - Component-scoped styling
- **Native Fetch API** - HTTP requests (no external dependencies)

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## 🔧 Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

3. **Build for production**:
   ```bash
   npm run build
   ```
   Output will be in the `dist/` folder

4. **Preview production build**:
   ```bash
   npm run preview
   ```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── itineraryApi.ts          # API client functions
│   ├── components/
│   │   ├── CustomerForm/            # Travel preference form
│   │   ├── DestinationCard/         # Single destination display
│   │   ├── ItineraryView/           # Full itinerary display
│   │   ├── LoadingState/            # Loading spinner
│   │   └── ErrorState/              # Error display with retry
│   ├── hooks/
│   │   └── useItinerary.ts          # Custom hook for workflow state
│   ├── types/
│   │   └── itinerary.ts             # TypeScript type definitions
│   ├── App.tsx                      # Main application component
│   ├── App.module.css               # App-level styles
│   ├── main.tsx                     # Entry point
│   └── index.css                    # Global styles
├── index.html                       # HTML template
├── vite.config.ts                   # Vite configuration (includes API proxy)
├── tsconfig.json                    # TypeScript configuration
├── package.json                     # Dependencies and scripts
└── README.md                        # This file
```

## 🔗 API Integration

The frontend connects to the backend via Vite's proxy configuration:

- **Development**: `/api/*` → `http://localhost:8000/api/*`
- **Production**: Configure your web server to proxy `/api/*` to the backend

### API Endpoints Used

1. **POST /api/itinerary**
   - Submits customer profile
   - Returns itinerary with destinations, POIs, events, weather

2. **GET /api/health**
   - Health check endpoint
   - Returns API status and version

## 🎨 Design

The UI uses a travel-themed color palette:
- **Primary**: Blue (#2196F3) - Trust, sky, water
- **Accents**: Teal, warm oranges
- **Backgrounds**: Clean whites with subtle gradients

CSS Modules ensure component-scoped styling with no conflicts.

## 📝 Usage Flow

1. **User fills out form** with travel preferences:
   - Interests (comma-separated)
   - Budget level
   - Travel dates
   - Party size
   - Departure city
   - Optional notes

2. **Form validation** ensures:
   - At least one interest
   - Valid date range
   - Party size ≥ 1
   - Non-empty departure city

3. **Submit triggers loading state** with spinner and message

4. **Success displays itinerary** with:
   - Multiple destinations
   - Each destination shows POIs, events, weather
   - All source URLs are clickable

5. **"Plan Another Trip" button** resets to form

## 🧪 Development

### Type Safety

All API contracts match the backend Pydantic models exactly using snake_case field names.

### Component Architecture

- **Presentational components**: Pure UI rendering (DestinationCard, LoadingState, ErrorState)
- **Container components**: State management and logic (App, CustomerForm)
- **Custom hooks**: Reusable stateful logic (useItinerary)

### Best Practices

- TypeScript strict mode enabled
- Proper error handling with descriptive messages
- Accessible forms with labels and error messages
- Responsive design with media queries
- Clean separation of concerns

## 🧪 Testing

The frontend includes 66 comprehensive tests across 8 test files using **Vitest + React Testing Library**:

### Test Coverage

- ✅ **Component Tests** (CustomerForm, ItineraryView, DestinationCard, LoadingState, ErrorState)
  - Rendering with props
  - User interactions (form submission, button clicks)
  - Conditional rendering based on state
  - Error boundary behaviors

- ✅ **Hook Tests** (useItinerary)
  - State machine transitions (idle → loading → success/error)
  - API call orchestration
  - Error handling and retry logic

- ✅ **API Client Tests**
  - `createItinerary()` request/response handling
  - `getHealth()` endpoint verification
  - Network error handling

- ✅ **Accessibility & UX Tests**
  - ARIA labels and semantic HTML
  - Keyboard navigation (Tab, Enter)
  - Screen reader support
  - Form validation feedback

### Running Tests

```bash
# Run all tests
npm run test

# Run with coverage report
npm run test -- --coverage

# Watch mode (re-run on changes)
npm run test -- --watch

# Run specific test file
npm run test -- CustomerForm.test.tsx

# Run tests matching pattern
npm run test -- --grep "form validation"
```

**Test Results:** All 66 tests passing ✅

## 🐛 Troubleshooting

**Issue**: "Failed to fetch" errors
- **Solution**: Ensure backend is running on `http://localhost:8000`

**Issue**: CORS errors
- **Solution**: Backend must include CORS middleware for `http://localhost:5173`

**Issue**: Build fails with TypeScript errors
- **Solution**: Run `npm install` to ensure all types are installed

## 📄 License

Part of the Boston Code Camp 40 Travel Agent project.

## 👥 Team

Built by Pris, the Frontend Specialist of the Blade Runner dev squad.
