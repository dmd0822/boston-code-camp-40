# Travel Agent AI - Frontend

This React + TypeScript single-page application lives in `src/frontend/`
and connects to the FastAPI backend to generate personalized travel
itineraries with destinations, points of interest, events, and weather
recommendations.

## 🚀 Features

- **Customer Profile Form**: Collects travel preferences including
  interests, budget, dates, party size, and departure city
- **AI-Powered Itinerary Generation**: Submits profiles to the backend
  and renders grounded itinerary recommendations
- **Rich Destination Cards**: Displays destination rationale, points of
  interest, events, weather guidance, and travel advisories
- **Responsive Design**: Works well on desktop and tablet layouts
- **State Management**: Clean idle → loading → success/error workflow
- **Accessible UI**: ARIA labels, keyboard navigation, and readable
  validation feedback
- **Container Runtime**: nginx proxies `/api/*` to the backend using a
  templated config at startup

## 🛠️ Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Development server and build tool
- **CSS Modules** - Component-scoped styling
- **Vitest + React Testing Library** - Frontend test stack
- **nginx + envsubst** - Production runtime and backend proxy wiring

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`
- Repository root at `C:\repos\boston-code-camp-40`

## 🔧 Setup

From the repository root:

1. **Install dependencies**
   ```bash
   cd src/frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`.

3. **Build for production**
   ```bash
   npm run build
   ```
   Output is written to `dist/`.

4. **Preview the production build**
   ```bash
   npm run preview
   ```

## 📁 Project Structure

```
src/frontend/
├── src/
│   ├── api/
│   │   └── itineraryApi.ts          # API client functions
│   ├── components/
│   │   ├── CustomerForm/            # Travel preference form
│   │   ├── DestinationCard/         # Single destination display
│   │   ├── TravelAdvisoryPanel/     # Detailed travel advisory view
│   │   ├── TravelAdvisoryBadge/     # Inline advisory level badge
│   │   ├── ErrorState/              # Error display and retry
│   │   ├── ItineraryView/           # Full itinerary display
│   │   └── LoadingState/            # Loading spinner
│   ├── hooks/
│   │   └── useItinerary.ts          # Workflow state hook
│   ├── types/
│   │   └── itinerary.ts             # Shared frontend types
│   ├── App.tsx                      # Main application component
│   ├── App.module.css               # App-level styles
│   ├── index.css                    # Global styles
│   └── main.tsx                     # Entry point
├── Dockerfile                       # Multi-stage Node → nginx image
├── entrypoint.sh                    # Injects BACKEND_URL/BACKEND_HOST
├── nginx.conf.template              # nginx proxy + SPA routing template
├── index.html                       # HTML template
├── package.json                     # Dependencies and scripts
├── tsconfig.json                    # TypeScript configuration
├── vite.config.ts                   # Vite dev proxy configuration
└── README.md                        # This file
```

## 🔗 API Integration

The frontend connects to the backend with relative `/api/*` requests.

- **Development**: Vite proxies `/api/*` → `http://localhost:8000`
- **Production**: `nginx.conf.template` is rendered by `entrypoint.sh`
  using `envsubst` so `BACKEND_URL` and `BACKEND_HOST` point the SPA to
  the deployed backend
- **TLS proxying**: nginx enables `proxy_ssl_server_name on` and sends
  the derived backend host for secure upstream routing

### API Endpoints Used

1. **POST `/api/itinerary`**
   - Submits customer profile data
   - Returns itinerary recommendations with destinations, POIs, events,
     weather, and travel advisories
2. **GET `/api/health`**
   - Checks backend health and version

## 🎨 Design

The UI uses a travel-themed palette with a focus on clarity, readable
cards, and fast handoff from form input to itinerary results. CSS
Modules keep component styling isolated.

## 📝 Usage Flow

1. **User fills out the form** with interests, budget, dates, party size,
   departure city, and optional notes
2. **Validation runs client-side** before submission
3. **Submit triggers loading state** and calls the backend API
4. **Success renders itinerary results** with destination details and
   supporting travel information
5. **Plan Another Trip** resets the workflow to the form

## 🧪 Development

### Type Safety

Frontend API contracts mirror the backend Pydantic models using
snake_case field names.

### Component Architecture

- **Presentational components**: DestinationCard, LoadingState,
  ErrorState
- **Stateful components**: App, CustomerForm, ItineraryView
- **Custom hooks**: `useItinerary` manages the request lifecycle

### Best Practices

- TypeScript strict mode enabled
- Relative `/api/*` requests only
- Accessible forms and validation messaging
- Responsive layouts with clear loading/error states
- Clean separation between API client, state, and presentation

## 🧪 Testing

The frontend includes **66 passing tests** across components, hooks, API
client behavior, and accessibility.

### Running Tests

```bash
cd src/frontend
npm run test
npm run test -- --coverage
npm run test:watch
npm run test -- CustomerForm.test.tsx
```

## 🐛 Troubleshooting

**Issue:** `Failed to fetch`
- **Solution:** Ensure the backend is running on `http://localhost:8000`

**Issue:** Proxying to the deployed backend fails
- **Solution:** Confirm `BACKEND_URL` is set correctly for the container
  and that `entrypoint.sh` rendered `nginx.conf.template`

**Issue:** Build fails with TypeScript errors
- **Solution:** Run `npm install` in `src/frontend/`

## 📄 License

Part of the Boston Code Camp 40 Travel Agent project.

## 👥 Team

Built by Pris, the Frontend Specialist of the Blade Runner dev squad.
