#!/usr/bin/env python3
"""
Test script for the SEPTA API module.
Run this to test the API functionality.
"""

import json
import os
from datetime import datetime
from modules.api import SEPTAAPI, get_next_trains, get_all_trains, get_arrivals


def save_raw_data(data, filename):
    """Save raw data to a JSON file without any modification."""
    # Create output directory if it doesn't exist
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{output_dir}/{timestamp}_{filename}.json"
    
    # Save raw data exactly as received
    with open(full_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Raw data saved to: {full_filename}")
    return full_filename


def test_next_to_arrive():
    """Test the NextToArrive API functionality."""
    print("=" * 60)
    print("Testing SEPTA NextToArrive API")
    print("=" * 60)
    
    api = SEPTAAPI()
    
    # Test case 1: Suburban Station to 30th Street Station
    print("\n1. Getting trains from Suburban Station to 30th Street Station:")
    trains = api.get_next_to_arrive("Suburban Station", "30th Street Station", 3)
    
    # Save raw data
    if trains:
        save_raw_data(trains, "next_to_arrive_suburban_to_30th")
        print(f"Found {len(trains)} trains:")
        for i, train in enumerate(trains, 1):
            print(f"\n{i}. {api.format_train_schedule(train)}")
    else:
        print("No trains found.")
    
    # Test case 2: Different route
    print("\n2. Getting trains from Market East to Temple University:")
    trains = api.get_next_to_arrive("Market East", "Temple University", 2)
    
    # Save raw data
    if trains:
        save_raw_data(trains, "next_to_arrive_market_east_to_temple")
        print(f"Found {len(trains)} trains:")
        for i, train in enumerate(trains, 1):
            print(f"\n{i}. {api.format_train_schedule(train)}")
    else:
        print("No trains found.")
    
    # Test case 3: Using convenience function
    print("\n3. Using convenience function (Suburban to 30th Street):")
    trains = get_next_trains("Suburban Station", "30th Street Station", 2)
    
    # Save raw data
    if trains:
        save_raw_data(trains, "convenience_function_suburban_to_30th")
        print(f"Found {len(trains)} trains:")
        for i, train in enumerate(trains, 1):
            print(f"\n{i}. {api.format_train_schedule(train)}")
    else:
        print("No trains found.")


def test_train_view():
    """Test the TrainView API functionality."""
    print("\n" + "=" * 60)
    print("Testing SEPTA TrainView API")
    print("=" * 60)
    
    api = SEPTAAPI()
    
    print("\nGetting all current trains in the system:")
    all_trains = api.get_train_view()
    
    # Save raw data
    if all_trains:
        save_raw_data(all_trains, "train_view_all_trains")
        print(f"Found {len(all_trains)} trains currently in the system.")
        
        # Show first 5 trains as examples
        print("\nFirst 5 trains:")
        for i, train in enumerate(all_trains[:5], 1):
            train_id = train.get('train_id', 'Unknown')
            origin = train.get('origin', 'Unknown')
            destination = train.get('destination', 'Unknown')
            status = train.get('status', 'Unknown')
            
            print(f"{i}. Train {train_id}: {origin} → {destination} | Status: {status}")
    else:
        print("No trains found or error occurred.")


def test_enhanced_search():
    """Test the enhanced search functionality."""
    print("\n" + "=" * 60)
    print("Testing Enhanced Search")
    print("=" * 60)
    
    api = SEPTAAPI()
    
    print("\nEnhanced search from Suburban Station to 30th Street Station:")
    enhanced_trains = api.search_trains_by_route("Suburban Station", "30th Street Station", 3)
    
    # Save raw data
    if enhanced_trains:
        save_raw_data(enhanced_trains, "enhanced_search_suburban_to_30th")
        print(f"Found {len(enhanced_trains)} enhanced train results:")
        for i, train in enumerate(enhanced_trains, 1):
            print(f"\n{i}. {api.format_train_schedule(train)}")
            
            # Show additional enhanced information if available
            if 'current_status' in train:
                print(f"   Current Status: {train.get('current_status', 'Unknown')}")
            if 'current_location' in train:
                print(f"   Current Location: {train.get('current_location', 'Unknown')}")
            if 'is_late' in train:
                print(f"   Is Late: {train.get('is_late', False)}")
    else:
        print("No enhanced results found.")


def test_arrivals():
    """Test the Arrivals API functionality."""
    print("\n" + "=" * 60)
    print("Testing SEPTA Arrivals API")
    print("=" * 60)
    
    api = SEPTAAPI()
    
    # Test case 1: Get arrivals for Suburban Station (Northbound)
    print("\n1. Getting arrivals for Suburban Station (Northbound):")
    arrivals = api.get_arrivals("Suburban Station", "N", 10)
    
    # Save raw data
    save_raw_data(arrivals, "arrivals_suburban_northbound")
    if arrivals:
        print(f"Found {len(arrivals)} arrivals:")
        for i, arrival in enumerate(arrivals[:5], 1):  # Show first 5
            train_id = arrival.get('train_id', 'Unknown')
            origin = arrival.get('origin', 'Unknown')
            arrival_time = arrival.get('arrival_time', 'Unknown')
            status = arrival.get('status', 'Unknown')
            
            print(f"{i}. Train {train_id}: {origin} → Suburban Station | Arrival: {arrival_time} | Status: {status}")
    else:
        print("No arrivals found.")
    
    # Test case 2: Get arrivals for 30th Street Station (Southbound)
    print("\n2. Getting arrivals for 30th Street Station (Southbound):")
    arrivals = api.get_arrivals("30th Street Station", "S", 8)
    
    # Save raw data
    save_raw_data(arrivals, "arrivals_30th_street_southbound")
    if arrivals:
        print(f"Found {len(arrivals)} arrivals:")
        for i, arrival in enumerate(arrivals[:5], 1):  # Show first 5
            train_id = arrival.get('train_id', 'Unknown')
            origin = arrival.get('origin', 'Unknown')
            arrival_time = arrival.get('arrival_time', 'Unknown')
            status = arrival.get('status', 'Unknown')
            
            print(f"{i}. Train {train_id}: {origin} → 30th Street Station | Arrival: {arrival_time} | Status: {status}")
    else:
        print("No arrivals found.")
    
    # Test case 3: Using convenience function
    print("\n3. Using convenience function (Market East arrivals):")
    arrivals = get_arrivals("Market East", "N", 5)
    
    # Save raw data
    save_raw_data(arrivals, "convenience_function_market_east_arrivals")
    if arrivals:
        print(f"Found {len(arrivals)} arrivals:")
        for i, arrival in enumerate(arrivals, 1):
            train_id = arrival.get('train_id', 'Unknown')
            origin = arrival.get('origin', 'Unknown')
            arrival_time = arrival.get('arrival_time', 'Unknown')
            
            print(f"{i}. Train {train_id}: {origin} → Market East | Arrival: {arrival_time}")
    else:
        print("No arrivals found.")


def test_arrivals_debug():
    """Debug test for the Arrivals API to capture raw responses and errors."""
    print("\n" + "=" * 60)
    print("DEBUG: Testing SEPTA Arrivals API with Raw Response Capture")
    print("=" * 60)
    
    api = SEPTAAPI()
    
    # Test the raw API call to see what we're actually getting
    print("\nDEBUG: Testing raw arrivals API call...")
    
    try:
        # Make a direct request to see the raw response
        import requests
        
        # Test different parameter combinations
        test_cases = [
            {"station": "Suburban Station", "direction": "N", "results": 10},
            {"station": "Suburban Station", "direction": "N", "results": 10, "req1": "Suburban Station"},
            {"station": "Suburban Station", "direction": "N", "results": 10, "req1": "Suburban Station", "req2": "N"},
            {"station": "Suburban Station", "direction": "N", "results": 10, "req1": "Suburban Station", "req2": "N", "req3": 10},
            # Test the working parameter format from next_to_arrive
            {"req1": "Suburban Station", "req2": "N", "req3": 10},
            {"req1": "Suburban Station", "req2": "30th Street Station", "req3": 10},  # This should work like next_to_arrive
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\nDEBUG Test Case {i}: Testing parameters: {params}")
            
            try:
                response = requests.get("https://www3.septa.org/api/Arrivals/index.php", params=params)
                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                print(f"Response URL: {response.url}")
                
                # Try to parse JSON
                try:
                    data = response.json()
                    print(f"Response Type: {type(data)}")
                    print(f"Response Length: {len(data) if isinstance(data, list) else 'Not a list'}")
                    
                    # Save raw response
                    save_raw_data({
                        "test_case": i,
                        "parameters": params,
                        "status_code": response.status_code,
                        "response_type": str(type(data)),
                        "response_length": len(data) if isinstance(data, list) else "Not a list",
                        "raw_data": data
                    }, f"debug_arrivals_test_case_{i}")
                    
                    if isinstance(data, list) and data:
                        print(f"First item: {data[0]}")
                    elif isinstance(data, dict):
                        print(f"Response keys: {list(data.keys())}")
                        print(f"Response content: {data}")
                    else:
                        print(f"Response content: {data}")
                        
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
                    print(f"Raw Response Text: {response.text[:500]}...")
                    
                    # Save raw text response
                    save_raw_data({
                        "test_case": i,
                        "parameters": params,
                        "status_code": response.status_code,
                        "error": "JSON decode error",
                        "raw_text": response.text
                    }, f"debug_arrivals_test_case_{i}_json_error")
                    
            except Exception as e:
                print(f"Request Error: {e}")
                save_raw_data({
                    "test_case": i,
                    "parameters": params,
                    "error": str(e)
                }, f"debug_arrivals_test_case_{i}_request_error")
                
    except Exception as e:
        print(f"Debug test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Also test the working method to compare
    print("\n" + "=" * 60)
    print("DEBUG: Comparing with working next_to_arrive method")
    print("=" * 60)
    
    try:
        print("\nTesting working next_to_arrive method...")
        working_trains = api.get_next_to_arrive("Suburban Station", "30th Street Station", 5)
        print(f"Working method returned {len(working_trains) if working_trains else 0} trains")
        
        if working_trains:
            save_raw_data(working_trains, "debug_working_next_to_arrive")
            print(f"First train: {working_trains[0]}")
        else:
            save_raw_data([], "debug_working_next_to_arrive_empty")
            print("Working method returned empty result")
            
    except Exception as e:
        print(f"Working method test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    try:
        test_next_to_arrive()
        test_train_view()
        test_enhanced_search()
        test_arrivals()
        test_arrivals_debug()  # Add debug test
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        print(f"Raw data has been saved to the 'test_output' directory.")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        print("Make sure you have an internet connection and the SEPTA API is accessible.")


if __name__ == "__main__":
    main()
