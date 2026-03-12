"""AI agents for travel recommendations.

This package contains the agent implementations:
- General Agent: Destination matching
- POI Agent: Points of interest discovery
- Event Agent: Festival and event discovery
- Weather Agent: Historical weather forecasting
"""

from .event_agent import create_event_agent, find_events
from .general_agent import create_general_agent, recommend_destinations
from .poi_agent import create_poi_agent, find_points_of_interest
from .weather_agent import create_weather_agent, get_weather_forecast

__all__ = [
    "create_general_agent",
    "recommend_destinations",
    "create_poi_agent",
    "find_points_of_interest",
    "create_event_agent",
    "find_events",
    "create_weather_agent",
    "get_weather_forecast",
]
