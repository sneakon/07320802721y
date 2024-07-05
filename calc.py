from fastapi import FastAPI, HTTPException
import requests
from collections import deque
import time

app = FastAPI()

# Configuration
window_size = 10
numbers_window = deque(maxlen=window_size)
current_average = 0.0

# Endpoint to handle number requests
@app.get("/numbers/{numberid}")
def get_numbers(numberid: str):
    global numbers_window, current_average
    
    # Define endpoint mappings for different number types
    endpoint_map = {
        'p': 'https://api.testserver.com/prime',
        'f': 'https://api.testserver.com/fibonacci',
        'e': 'https://api.testserver.com/even',
        'r': 'https://api.testserver.com/random'
    }
    
    # Check if numberid is valid
    if numberid not in endpoint_map:
        raise HTTPException(status_code=400, detail="Invalid numberid. Use 'p', 'f', 'e', or 'r'.")

    # Fetch numbers from the test server
    try:
        start_time = time.time()
        response = requests.get(endpoint_map[numberid], timeout=0.5)  # Timeout set to 500 ms
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            numbers = response.json()["numbers"]
            unique_numbers = set(numbers)  # Ensure numbers are unique
            
            # Add unique numbers to the window
            for num in unique_numbers:
                if len(numbers_window) < window_size:
                    numbers_window.append(num)
                else:
                    numbers_window.popleft()  # Remove oldest number
                    numbers_window.append(num)
            
            # Update current_average
            current_average = sum(numbers_window) / len(numbers_window) if numbers_window else 0.0
            
            # Prepare response
            response_data = {
                "numbers_received": numbers,
                "previous_window_state": list(numbers_window),
                "current_window_state": list(numbers_window),
                "average": current_average
            }
            
            return response_data
        
        elif elapsed_time > 0.5:
            raise HTTPException(status_code=500, detail="Request to test server timed out (>500 ms).")
        
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching numbers from test server.")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to test server failed: {str(e)}")

