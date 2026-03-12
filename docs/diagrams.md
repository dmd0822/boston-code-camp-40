# Travel Agent Application — Architecture Diagrams

> **Source:** Auto-generated from [architecture.md](architecture.md) — update when architecture changes.

This document provides visual representations of the Travel Agent Application architecture using Mermaid diagrams. Each diagram focuses on a specific aspect of the system for clarity and maintainability.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Frontend Component Architecture](#2-frontend-component-architecture)
3. [Agent Orchestration Sequence](#3-agent-orchestration-sequence)
4. [Data Flow Pipeline](#4-data-flow-pipeline)
5. [Pydantic Model Class Diagram](#5-pydantic-model-class-diagram)
6. [API Request/Response Flow](#6-api-requestresponse-flow)
7. [Infrastructure Diagram](#7-infrastructure-diagram)
8. [Error Handling Flow](#8-error-handling-flow)

---

## 1. System Overview

High-level architecture showing the complete system from React frontend through to external services.

```mermaid
graph TD
    User[User Browser] -->|HTTPS| Frontend[React Frontend<br/>Vite + TypeScript<br/>State-driven Components]
    Frontend -->|POST /api/itinerary| Backend[FastAPI Backend]
    Backend --> Orchestrator[Travel Orchestrator]
    
    Orchestrator -->|Phase 1: Sequential| GeneralAgent[General Agent<br/>Destination Matching]
    
    Orchestrator -->|Phase 2: Concurrent| POIAgent[POI Agent<br/>Points of Interest]
    Orchestrator -->|Phase 2: Concurrent| EventAgent[Event Agent<br/>Festivals & Events]
    Orchestrator -->|Phase 2: Concurrent| WeatherAgent[Weather Agent<br/>Historical Forecasts]
    
    GeneralAgent -->|Tool Call| AzureOpenAI[Azure OpenAI<br/>GPT-4o]
    POIAgent -->|Tool Call| AzureOpenAI
    EventAgent -->|Tool Call| AzureOpenAI
    WeatherAgent -->|Tool Call| AzureOpenAI
    
    GeneralAgent -->|search_web| BingSearch[Bing Web Search API<br/>Grounding]
    POIAgent -->|search_web| BingSearch
    EventAgent -->|search_web| BingSearch
    WeatherAgent -->|search_web| BingSearch
    
    Orchestrator -->|Aggregated Response| Backend
    Backend -->|200 OK JSON| Frontend
    Frontend -->|Display Itinerary| User
    
    style Orchestrator fill:#e1f5ff
    style GeneralAgent fill:#fff4e1
    style POIAgent fill:#f0e1ff
    style EventAgent fill:#f0e1ff
    style WeatherAgent fill:#f0e1ff
    style AzureOpenAI fill:#ffe1e1
    style BingSearch fill:#ffe1e1
```

**Key Points:**
- React frontend with complete component architecture (see Frontend Component Architecture diagram)
- Orchestrator coordinates two-phase agent execution
- All agents grounded in Bing Web Search (mandatory search-first pattern)
- Azure OpenAI (GPT-4o) provides reasoning for all agents

---

## 2. Frontend Component Architecture

Complete Phase 4 frontend component structure showing state management, conditional rendering, and API integration.

```mermaid
graph TD
    App[App.tsx<br/>Root Component] -->|uses| UseItinerary[useItinerary Hook<br/>State Management]
    
    UseItinerary -->|manages states| States{Application State}
    UseItinerary -->|calls| API[itineraryApi.ts<br/>API Client]
    
    States -->|idle| CustomerForm[CustomerForm Component<br/>User Input Form]
    States -->|loading| LoadingState[LoadingState Component<br/>Spinner + Progress Text]
    States -->|success| ItineraryView[ItineraryView Component<br/>Results Display]
    States -->|error| ErrorState[ErrorState Component<br/>Error Message]
    
    CustomerForm -->|onSubmit| UseItinerary
    ErrorState -->|retry| UseItinerary
    
    ItineraryView -->|maps| DestinationCards[DestinationCard Components<br/>One per Destination]
    
    subgraph "DestinationCard Content"
        DestinationCards --> POIs[POI List<br/>Points of Interest]
        DestinationCards --> Events[Event List<br/>Festivals & Activities]
        DestinationCards --> Weather[Weather Widget<br/>Forecast Display]
    end
    
    API -->|fetch POST| APIBoundary[/api/itinerary<br/>REST Endpoint]
    APIBoundary -.->|200 OK JSON| API
    APIBoundary -.->|4xx/5xx Error| API
    
    subgraph "State Transitions"
        Idle[idle: Initial] --> Loading[loading: API Call]
        Loading --> Success[success: Data Received]
        Loading --> Error[error: Request Failed]
        Error --> Idle2[idle: After Retry]
    end
    
    style App fill:#e1f5ff
    style UseItinerary fill:#fff4e1
    style States fill:#f0e1ff
    style ItineraryView fill:#e1ffe1
    style CustomerForm fill:#e1f5ff
    style LoadingState fill:#fff4e1
    style ErrorState fill:#ffe1e1
    style API fill:#f0e1ff
    style APIBoundary fill:#ffe1e1
```

**Component Responsibilities:**

1. **App.tsx**: Root component that renders based on `useItinerary` state
2. **useItinerary Hook**: Manages application state lifecycle (idle → loading → success/error)
3. **CustomerForm**: Collects user preferences (interests, budget, dates, party size)
4. **LoadingState**: Displays loading spinner with status text during API call
5. **ItineraryView**: Renders successful response with destination cards
6. **DestinationCard**: Shows POIs, events, and weather for each destination
7. **ErrorState**: Displays error message with retry button
8. **itineraryApi.ts**: Type-safe API client using fetch (POST to `/api/itinerary`)

**State Machine Flow:**
- **idle**: Initial state; shows CustomerForm
- **loading**: API call in progress; shows LoadingState
- **success**: Data received; shows ItineraryView
- **error**: Request failed; shows ErrorState with retry → back to idle

**API Boundary:**
- Frontend sends `CustomerProfile` JSON
- Backend returns `ItineraryResponse` with destinations array
- Error handling: 4xx/5xx responses trigger error state

---

## 3. Agent Orchestration Sequence

Detailed sequence diagram showing the two-phase orchestration flow with timing.

```mermaid
sequenceDiagram
    participant Client as React Client
    participant API as FastAPI Backend
    participant Orch as Travel Orchestrator
    participant Gen as General Agent
    participant POI as POI Agent
    participant Event as Event Agent
    participant Weather as Weather Agent
    participant OpenAI as Azure OpenAI
    participant Bing as Bing Search API

    Client->>API: POST /api/itinerary<br/>(CustomerProfile)
    API->>Orch: create_itinerary(profile)
    
    Note over Orch,Gen: Phase 1: Sequential
    Orch->>Gen: run(CustomerProfile)
    Gen->>Bing: search_web("best destinations for...")
    Bing-->>Gen: Search results (JSON)
    Gen->>OpenAI: Analyze results + prompt
    OpenAI-->>Gen: List[Destination] (3-4 items)
    Gen-->>Orch: List[Destination]
    
    Note over Orch,Weather: Phase 2: Concurrent Fan-Out
    par Concurrent Execution
        Orch->>POI: run(Destination + dates)
        POI->>Bing: search_web("top things to do in...")
        Bing-->>POI: POI search results
        POI->>OpenAI: Extract POIs from results
        OpenAI-->>POI: List[PointOfInterest]
        POI-->>Orch: List[PointOfInterest]
    and
        Orch->>Event: run(Destination + dates)
        Event->>Bing: search_web("events festivals in...")
        Bing-->>Event: Event search results
        Event->>OpenAI: Extract events in date range
        OpenAI-->>Event: List[Event]
        Event-->>Orch: List[Event]
    and
        Orch->>Weather: run(Destination + dates)
        Weather->>Bing: search_web("average weather in...")
        Bing-->>Weather: Weather search results
        Weather->>OpenAI: Extract historical averages
        OpenAI-->>Weather: WeatherForecast
        Weather-->>Orch: WeatherForecast
    end
    
    Note over Orch: Fan-In: Aggregate Results
    Orch->>Orch: Build ItineraryResponse
    Orch-->>API: ItineraryResponse
    API-->>Client: 200 OK (JSON itinerary)
    
    Note over Client,API: Total Time: 15-30 seconds
```

**Timing:**
- Phase 1 (General Agent): ~5-10 seconds
- Phase 2 (Specialists): ~5-10 seconds (parallel execution)
- Total: 15-30 seconds end-to-end

---

## 4. Data Flow Pipeline

How customer data transforms through the agent pipeline into a complete itinerary.

```mermaid
graph LR
    Input[CustomerProfile<br/>interests, budget<br/>dates, party size] --> Gen[General Agent]
    
    Gen -->|3-4 destinations| Dest1[Destination 1]
    Gen --> Dest2[Destination 2]
    Gen --> Dest3[Destination 3]
    
    subgraph " "
        Dest1 --> POI1[POI Agent]
        Dest1 --> Event1[Event Agent]
        Dest1 --> Weather1[Weather Agent]
        
        POI1 --> POIList1[List&lt;PointOfInterest&gt;]
        Event1 --> EventList1[List&lt;Event&gt;]
        Weather1 --> Forecast1[WeatherForecast]
    end
    
    subgraph " "
        Dest2 --> POI2[POI Agent]
        Dest2 --> Event2[Event Agent]
        Dest2 --> Weather2[Weather Agent]
        
        POI2 --> POIList2[List&lt;PointOfInterest&gt;]
        Event2 --> EventList2[List&lt;Event&gt;]
        Weather2 --> Forecast2[WeatherForecast]
    end
    
    subgraph " "
        Dest3 --> POI3[POI Agent]
        Dest3 --> Event3[Event Agent]
        Dest3 --> Weather3[Weather Agent]
        
        POI3 --> POIList3[List&lt;PointOfInterest&gt;]
        Event3 --> EventList3[List&lt;Event&gt;]
        Weather3 --> Forecast3[WeatherForecast]
    end
    
    POIList1 --> Agg[Aggregation]
    EventList1 --> Agg
    Forecast1 --> Agg
    POIList2 --> Agg
    EventList2 --> Agg
    Forecast2 --> Agg
    POIList3 --> Agg
    EventList3 --> Agg
    Forecast3 --> Agg
    
    Agg --> Output[ItineraryResponse<br/>Complete enriched itinerary]
    
    style Input fill:#e1f5ff
    style Gen fill:#fff4e1
    style Agg fill:#e1ffe1
    style Output fill:#e1f5ff
```

**Transformations:**
1. **CustomerProfile** → General Agent → **List[Destination]** (3-4 items)
2. Each **Destination** → 3 specialist agents (concurrent)
   - POI Agent → **List[PointOfInterest]**
   - Event Agent → **List[Event]**
   - Weather Agent → **WeatherForecast**
3. All outputs → Deterministic merge → **ItineraryResponse**

---

## 5. Pydantic Model Class Diagram

Data model relationships showing composition and aggregation patterns.

```mermaid
classDiagram
    class CustomerProfile {
        +List~str~ interests
        +str budget
        +TravelDates travel_dates
        +int party_size
        +str departure_city
        +Optional~str~ notes
    }
    
    class TravelDates {
        +date start
        +date end
    }
    
    class ItineraryResponse {
        +str itinerary_id
        +List~Destination~ destinations
        +datetime generated_at
    }
    
    class Destination {
        +str name
        +str country
        +str rationale
        +str source_url
        +List~PointOfInterest~ pois
        +List~Event~ events
        +WeatherForecast weather_forecast
    }
    
    class PointOfInterest {
        +str name
        +str description
        +str category
        +float visit_duration_hours
        +str source_url
    }
    
    class Event {
        +str name
        +EventDates dates
        +str description
        +str venue
        +str source_url
    }
    
    class EventDates {
        +date start
        +date end
    }
    
    class WeatherForecast {
        +int avg_high_celsius
        +int avg_low_celsius
        +str precipitation_chance
        +str clothing_suggestion
        +str source_url
    }
    
    CustomerProfile *-- TravelDates : contains
    ItineraryResponse *-- Destination : contains 3-4
    Destination *-- PointOfInterest : contains many
    Destination *-- Event : contains many
    Destination *-- WeatherForecast : contains one
    Event *-- EventDates : contains
```

**Model Locations:**
- All models defined in `src/api/models/`
- Shared between API routes and agent orchestrator
- Single source of truth for data contracts

---

## 6. API Request/Response Flow

HTTP layer showing endpoint routing, validation, and error handling.

```mermaid
graph TD
    Start[Client Request] --> Route{Route?}
    
    Route -->|GET /api/health| Health[Health Check Handler]
    Route -->|POST /api/itinerary| Validate[Pydantic Validation]
    Route -->|Other| NotFound[404 Not Found]
    
    Health --> HealthOK[200 OK<br/>status: healthy, version]
    
    Validate -->|Valid| Orchestrator[Call Orchestrator]
    Validate -->|Invalid| BadRequest[400 Bad Request<br/>Validation errors]
    
    Orchestrator -->|Success| BuildResponse[Build ItineraryResponse]
    Orchestrator -->|Agent Failure| ServerError{Error Type?}
    
    ServerError -->|General Agent Fails| EmptyItinerary[200 OK<br/>Empty itinerary + error flag]
    ServerError -->|Specialist Fails| PartialItinerary[200 OK<br/>Partial results + error flag]
    ServerError -->|Orchestrator Error| InternalError[500 Internal Server Error]
    ServerError -->|Upstream Unavailable| ServiceUnavail[503 Service Unavailable]
    
    BuildResponse --> Success[200 OK<br/>Full ItineraryResponse JSON]
    
    style Validate fill:#e1f5ff
    style Orchestrator fill:#fff4e1
    style Success fill:#e1ffe1
    style BadRequest fill:#ffe1e1
    style InternalError fill:#ffe1e1
    style ServiceUnavail fill:#ffe1e1
```

**Error Handling Strategy:**
- **400**: Invalid input (Pydantic validation failure)
- **500**: Orchestrator or unhandled error
- **503**: Azure OpenAI or Bing Search unavailable
- **Partial Success**: Specialist agent failures return partial itinerary (not 500)

---

## 7. Infrastructure Diagram

Azure deployment architecture showing all managed services and container apps.

```mermaid
graph TB
    subgraph "Azure Resource Group"
        subgraph "Container Apps Environment"
            FrontendApp[Azure Container App<br/>Frontend - React SPA<br/>nginx serving static files]
            BackendApp[Azure Container App<br/>Backend - FastAPI<br/>Python + Uvicorn]
        end
        
        ACR[Azure Container Registry<br/>Stores Docker images<br/>frontend:latest, backend:latest]
        
        OpenAI[Azure OpenAI Service<br/>GPT-4o deployment<br/>S0 tier]
        
        Bing[Bing Web Search<br/>Cognitive Services<br/>S1 tier]
        
        KeyVault[Azure Key Vault<br/>Secrets Management<br/>Optional for MVP]
    end
    
    Internet[Internet Users] -->|HTTPS| FrontendApp
    FrontendApp -->|/api/* proxy| BackendApp
    
    BackendApp -->|API calls| OpenAI
    BackendApp -->|search_web tool| Bing
    
    ACR -.->|Pull images| FrontendApp
    ACR -.->|Pull images| BackendApp
    
    BackendApp -.->|Read secrets| KeyVault
    
    style FrontendApp fill:#e1f5ff
    style BackendApp fill:#fff4e1
    style OpenAI fill:#ffe1e1
    style Bing fill:#ffe1e1
    style ACR fill:#f0e1ff
    style KeyVault fill:#e1ffe1
```

**Resource Summary:**
- **Container Apps**: Consumption tier (auto-scale)
- **Azure OpenAI**: GPT-4o model deployment
- **Bing Search**: S1 tier (grounding for all agents)
- **ACR**: Basic tier (image storage)
- **Key Vault**: Optional (MVP uses env vars)

**IaC:** All infrastructure defined in Bicep templates (`infra/main.bicep` and modules)

---

## 8. Error Handling Flow

How the system handles failures at different layers of the agent pipeline.

```mermaid
graph TD
    Start[Orchestrator Start] --> GenAgent[Call General Agent]
    
    GenAgent -->|Success| Destinations[List&lt;Destination&gt;<br/>3-4 items]
    GenAgent -->|Failure| GenFail[General Agent Failed]
    
    GenFail -->|Max retries exceeded| EmptyResponse[Return Empty Itinerary<br/>error_message: General agent failed]
    
    Destinations --> FanOut[Fan-Out to Specialists<br/>POI, Event, Weather]
    
    FanOut --> POICall[POI Agent]
    FanOut --> EventCall[Event Agent]
    FanOut --> WeatherCall[Weather Agent]
    
    POICall -->|Success| POISuccess[List&lt;PointOfInterest&gt;]
    POICall -->|Failure| POIFail[Empty POI list]
    
    EventCall -->|Success| EventSuccess[List&lt;Event&gt;]
    EventCall -->|Failure| EventFail[Empty Event list]
    
    WeatherCall -->|Success| WeatherSuccess[WeatherForecast]
    WeatherCall -->|Failure| WeatherFail[Null weather]
    
    POISuccess --> Merge[Merge Results]
    POIFail --> Merge
    EventSuccess --> Merge
    EventFail --> Merge
    WeatherSuccess --> Merge
    WeatherFail --> Merge
    
    Merge --> Check{All Agents<br/>Succeeded?}
    
    Check -->|Yes| FullItinerary[Return Full Itinerary<br/>200 OK]
    Check -->|Partial| PartialItinerary[Return Partial Itinerary<br/>200 OK with warnings]
    
    subgraph "JSON Parse Failures"
        ParseFail[LLM Returns Invalid JSON] -->|Retry 1| Retry1[Re-invoke Agent]
        Retry1 -->|Still Invalid| Retry2[Retry 2]
        Retry2 -->|Max Retries| UsePartial[Use Partial Result<br/>Log error]
    end
    
    style GenFail fill:#ffe1e1
    style POIFail fill:#fff4e1
    style EventFail fill:#fff4e1
    style WeatherFail fill:#fff4e1
    style EmptyResponse fill:#ffe1e1
    style PartialItinerary fill:#fff4e1
    style FullItinerary fill:#e1ffe1
```

**Failure Handling Principles:**
1. **General Agent Failure**: Returns empty itinerary (can't proceed without destinations)
2. **Specialist Agent Failure**: Other agents still run; return partial enrichment
3. **JSON Parse Failure**: Retry up to 2 times, then return partial result
4. **Upstream Unavailable**: Return 503 Service Unavailable (not 500)
5. **Partial Success > Total Failure**: User gets some results even if one agent fails

---

## Maintenance Notes

### Updating Diagrams

When architecture changes:
1. Update `docs/architecture.md` first (single source of truth)
2. Update relevant diagrams in this file
3. Test Mermaid syntax with a live editor ([mermaid.live](https://mermaid.live/))
4. Commit both files together

### Diagram Conventions

- **Color coding:**
  - Blue (#e1f5ff): User-facing components (Frontend, API)
  - Yellow (#fff4e1): Orchestration and agent logic
  - Purple (#f0e1ff): Specialist agents
  - Red (#ffe1e1): External services (Azure OpenAI, Bing)
  - Green (#e1ffe1): Success states / outputs

- **Node labels**: Keep concise; use line breaks (`<br/>`) for multi-line labels
- **Arrows**: Solid for data flow, dashed for infrastructure relationships

### Related Documentation

- [architecture.md](architecture.md) — Detailed architecture specification
- [README.md](../README.md) — Project overview and quick start
- [.squad/decisions.md](../.squad/decisions.md) — Team architectural decisions
