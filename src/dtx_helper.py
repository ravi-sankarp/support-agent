import requests
import jwt
import datetime
import os
from typing import Optional, Dict, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration from environment variables
DTX_BASE_URL = os.getenv("DTX_BASE_URL")
LOGIN_EMAIL = os.getenv("DTX_LOGIN_EMAIL") 
LOGIN_PASSWORD = os.getenv("DTX_LOGIN_PASSWORD")
TENANT_ID = os.getenv("DTX_TENANT_ID")


class DtxHelper:
    def __init__(self):
        self.login_token: Optional[str] = None
        self.tenant_token: Optional[str] = None
        
        # Validate required environment variables
        if not all([DTX_BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD, TENANT_ID]):
            missing = []
            if not DTX_BASE_URL: missing.append("DTX_BASE_URL")
            if not LOGIN_EMAIL: missing.append("DTX_LOGIN_EMAIL")
            if not LOGIN_PASSWORD: missing.append("DTX_LOGIN_PASSWORD") 
            if not TENANT_ID: missing.append("DTX_TENANT_ID")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    async def _login_to_dtx(self) -> None:
        """Private method to login to DTX and get login token."""
        try:
            url = f"{DTX_BASE_URL}/user/login"
            payload = {
                "email": LOGIN_EMAIL,
                "password": LOGIN_PASSWORD
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.login_token = data.get("message")
            
        except requests.RequestException as err:
            raise Exception(f"DTX-LOGIN-ERROR: {err}")

    async def _generate_tenant_token(self) -> None:
        """Private method to generate tenant token using login token."""
        if not self.login_token:
            raise ValueError("Not logged in")
            
        try:
            url = f"{DTX_BASE_URL}/user/tokenExchange"
            headers = {
                "Authorization": f"Bearer {self.login_token}"
            }
            payload = {
                "tenantId": TENANT_ID
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.tenant_token = data.get("message")
            
        except requests.RequestException as err:
            raise Exception(f"TENANT-TOKEN-ERROR: {err}")

    def _is_token_expired(self, token: str) -> bool:
        """Check if JWT token is expired with 1 hour buffer."""
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = decoded.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.datetime.fromtimestamp(exp_timestamp)
                buffer_time = datetime.datetime.now() + datetime.timedelta(hours=1)
                return buffer_time >= exp_datetime
            return True
        except Exception:
            return True

    async def get_tenant_token(self) -> str:
        """Get tenant token, refreshing if not available or expired."""
        if not self.tenant_token or self._is_token_expired(self.tenant_token):
            await self.init_session()
        return self.tenant_token

    async def init_session(self) -> None:
        """Initialize session by logging in and generating tenant token."""
        await self._login_to_dtx()
        await self._generate_tenant_token()

    async def create_feedback_form(self, email: str, positives: str, improvements: str) -> Dict[str, Any]:
        """Create a feedback form with the provided data."""
        # Format data for DTX API
        form_data = [
            {
                "templateId": "130741b5-fefe-432a-aa54-2b514ec657e4",
                "dueDate": (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                "inputPayload": [
                    {
                        "field_id": "4d67f636-8f85-4301-841a-6c8bec17ca15",
                        "value": email.strip()
                    },
                    {
                        "field_id": "ecef71bc-3264-4060-b3a5-cf5aee6dc873", 
                        "value": positives.strip()
                    },
                    {
                        "field_id": "39a1d019-e435-471d-8850-4cb6c8aad4fc",
                        "value": improvements.strip()
                    }
                ],
                "status": 1
            }
        ]
        
        return await self.create_form(form_data)

    async def create_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a form using the tenant token."""
        token = await self.get_tenant_token()
        
        try:
            url = f"{DTX_BASE_URL}/forms"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=form_data)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as err:
            raise Exception(f"CREATE-FORM-ERROR: {err}")