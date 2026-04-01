import requests

class APIClient:
    """Simple HTTP client for backend communication"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze(self, user_input, username):
        """Send text for analysis"""
        try:
            response = requests.post(
                f"{self.base_url}/analyze",
                json={"user_input": user_input, "username": username},
                timeout=30
            )
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to analyze: {str(e)}")

    def analyze_game(self, username, game_data, duration_minutes):
        """Send game metrics for analysis"""
        try:
            response = requests.post(
                f"{self.base_url}/analyze-game",
                json={
                    "username": username,
                    "game_data": game_data,
                    "duration_minutes": duration_minutes
                },
                timeout=30
            )
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to analyze game: {str(e)}")
    
    def save_session(self, username, initial_metrics, final_metrics, technique, duration):
        """Save session data"""
        try:
            response = requests.post(
                f"{self.base_url}/save-session",
                json={
                    "username": username,
                    "initial_metrics": initial_metrics,
                    "final_metrics": final_metrics,
                    "technique": technique,
                    "duration": duration
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"[WARNING] Failed to save session: {e}")
            return None
    
    def get_sessions(self, username):
        """Get user's session history"""
        try:
            response = requests.get(
                f"{self.base_url}/get-sessions/{username}",
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"[WARNING] Failed to get sessions: {e}")
            return {"sessions": []}
