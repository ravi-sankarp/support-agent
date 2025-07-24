import requests
import jwt
import datetime
from typing import Optional, Dict, Any

# Global configuration
DTX_BASE_URL = "your_dtx_base_url_here"
LOGIN_EMAIL = "your_email_here"
LOGIN_PASSWORD = "your_password_here"
TENANT_ID = "your_tenant_id_here"


class DtxHelper:
    def __init__(self):
        self.login_token: Optional[str] = None
        self.tenant_token: Optional[str] = None

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