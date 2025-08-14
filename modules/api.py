import requests
import json
from typing import List, Dict, Optional
from datetime import datetime


class SEPTAAPI:
    """SEPTA Regional Rail API client for accessing train data."""
    
    # Base URLs for SEPTA APIs
    BASE_URL = "https://www3.septa.org/api"
    NEXT_TO_ARRIVE_URL = f"{BASE_URL}/NextToArrive/index.php"
    TRAIN_VIEW_URL = f"{BASE_URL}/TrainView/index.php"
    ARRIVALS_DEPARTURES_URL = f"{BASE_URL}/Arrivals/index.php"
    ARRIVALS_URL = f"{BASE_URL}/Arrivals/index.php"
    
    def __init__(self):
        """Initialize the SEPTA API client."""
        self.session = requests.Session()
        # Set headers to mimic a browser request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def get_next_to_arrive(self, 
                          from_station: str, 
                          to_station: str, 
                          num_results: int = 10) -> List[Dict]:
        """
        Get departure and arrival times between two stations.
        
        Args:
            from_station: Starting station ID or name
            to_station: Ending station ID or name  
            num_results: Number of results to return (default: 10)
            
        Returns:
            List of train schedules between the stations
            
        Example:
            >>> api = SEPTAAPI()
            >>> trains = api.get_next_to_arrive("Suburban Station", "30th Street Station", 5)
        """
        try:
            params = {
                'req1': from_station,
                'req2': to_station,
                'req3': num_results
            }
            
            response = self.session.get(self.NEXT_TO_ARRIVE_URL, params=params)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Handle case where API returns error message
            if isinstance(data, dict) and 'error' in data:
                raise Exception(f"SEPTA API Error: {data['error']}")
            
            return data if isinstance(data, list) else []
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def get_train_view(self) -> List[Dict]:
        """
        Get information on all current regional rail trains.
        
        Returns:
            List of all trains currently in the system
        """
        try:
            response = self.session.get(self.TRAIN_VIEW_URL)
            response.raise_for_status()
            
            data = response.json()
            return data if isinstance(data, list) else []
            
        except Exception as e:
            print(f"Error getting train view: {e}")
            return []
    
    def get_station_arrivals_departures(self, 
                                      station: str, 
                                      direction: str = "N", 
                                      num_results: int = 10) -> List[Dict]:
        """
        Get arrivals and departures for a specific station.
        
        Args:
            station: Station ID or name
            direction: Direction - "N" for Northbound, "S" for Southbound
            num_results: Number of results to return
            
        Returns:
            List of arrivals and departures for the station
        """
        try:
            params = {
                'station': station,
                'results': num_results,
                'direction': direction
            }
            
            response = self.session.get(self.ARRIVALS_DEPARTURES_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data if isinstance(data, list) else []
            
        except Exception as e:
            print(f"Error getting station arrivals/departures: {e}")
            return []
    
    def get_arrivals(self, 
                    station: str, 
                    direction: str = "N", 
                    num_results: int = 20,
                    include_departures: bool = False) -> List[Dict]:
        """
        Get real-time arrivals for a specific station.
        This endpoint focuses specifically on arrivals data.
        
        Args:
            station: Station ID or name
            direction: Direction - "N" for Northbound, "S" for Southbound
            num_results: Number of results to return (default: 20)
            include_departures: Whether to include departure information (default: False)
            
        Returns:
            List of arrival information for the station
            
        Example:
            >>> api = SEPTAAPI()
            >>> arrivals = api.get_arrivals("Suburban Station", "N", 10)
        """
        try:
            params = {
                'station': station,
                'results': num_results,
                'direction': direction
            }
            
            # If we want arrivals only, we can filter the response
            response = self.session.get(self.ARRIVALS_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not isinstance(data, list):
                return []
            
            # Filter for arrivals if requested
            if not include_departures:
                # Filter to show only arrivals (trains coming TO this station)
                arrivals = []
                for item in data:
                    # Check if this is an arrival (train coming to the station)
                    if 'arrival_time' in item and item.get('arrival_time'):
                        arrivals.append(item)
                return arrivals
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Request error getting arrivals: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error getting arrivals: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error getting arrivals: {e}")
            return []
    
    def search_trains_by_route(self, from_station: str, to_station: str, 
                              max_results: int = 20) -> List[Dict]:
        """
        Enhanced search that combines multiple API calls for comprehensive train data.
        
        Args:
            from_station: Starting station
            to_station: Ending station
            max_results: Maximum number of results to return
            
        Returns:
            List of train schedules with enhanced information
        """
        # Get next to arrive data
        next_trains = self.get_next_to_arrive(from_station, to_station, max_results)
        
        # Get current train view for additional context
        all_trains = self.get_train_view()
        
        # Enhance the data with additional train information
        enhanced_results = []
        for train in next_trains:
            enhanced_train = train.copy()
            
            # Try to find additional info from train view
            if 'train_id' in train:
                for view_train in all_trains:
                    if view_train.get('train_id') == train['train_id']:
                        enhanced_train.update({
                            'current_status': view_train.get('status', 'Unknown'),
                            'current_location': view_train.get('current_location', 'Unknown'),
                            'is_late': view_train.get('is_late', False)
                        })
                        break
            
            enhanced_results.append(enhanced_train)
        
        return enhanced_results
    
    def format_train_schedule(self, train_data: Dict) -> str:
        """
        Format train schedule data into a readable string.
        
        Args:
            train_data: Dictionary containing train schedule information
            
        Returns:
            Formatted string representation of the train schedule
        """
        try:
            # Extract key information
            train_id = train_data.get('train_id', 'Unknown')
            origin = train_data.get('origin', 'Unknown')
            destination = train_data.get('destination', 'Unknown')
            departure_time = train_data.get('departure_time', 'Unknown')
            arrival_time = train_data.get('arrival_time', 'Unknown')
            delay = train_data.get('delay', '0')
            
            # Format the schedule
            schedule = f"Train {train_id}: {origin} → {destination}\n"
            schedule += f"Departure: {departure_time} | Arrival: {arrival_time}"
            
            if delay and delay != '0':
                schedule += f" | Delay: {delay} min"
            
            return schedule
            
        except Exception as e:
            print(f"Error formatting train schedule: {e}")
            return "Error formatting schedule"


# Convenience functions for quick access
def get_next_trains(from_station: str, to_station: str, num_results: int = 10) -> List[Dict]:
    """Quick function to get next trains between stations."""
    api = SEPTAAPI()
    return api.get_next_to_arrive(from_station, to_station, num_results)


def get_all_trains() -> List[Dict]:
    """Quick function to get all current trains."""
    api = SEPTAAPI()
    return api.get_train_view()


def get_arrivals(station: str, direction: str = "N", num_results: int = 20) -> List[Dict]:
    """Quick function to get arrivals for a specific station."""
    api = SEPTAAPI()
    return api.get_arrivals(station, direction, num_results)


if __name__ == "__main__":
    # Example usage
    api = SEPTAAPI()
    
    # Get trains from Suburban Station to 30th Street Station
    print("Getting trains from Suburban Station to 30th Street Station...")
    trains = api.get_next_to_arrive("Suburban Station", "30th Street Station", 5)
    
    if trains:
        print(f"Found {len(trains)} trains:")
        for train in trains:
            print(api.format_train_schedule(train))
            print("-" * 50)
    else:
        print("No trains found or error occurred.")
