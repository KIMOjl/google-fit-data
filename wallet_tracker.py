#!/usr/bin/env python3
"""
Google Wallet Transaction Tracker
Monitors specific card expenses using Google Pay/Wallet APIs.
"""

import json
import os
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from env_utils import load_dotenv

load_dotenv()

# Google Pay API endpoints (limited access)
# Note: Full Wallet API requires special Google partnership
# But we can use Google Pay APIs for transaction history

class WalletTracker:
    def __init__(self):
        self.token_path = Path(os.environ.get("TOKEN_PATH", "credentials/google-fit-token.json"))
        self.transactions_file = Path("/home/openclaw/.openclaw/workspace/data/transactions.json")
        self.transactions_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_tokens(self):
        """Load current OAuth tokens."""
        with open(self.token_path) as f:
            return json.load(f)
    
    def check_pay_api_access(self):
        """Check if we can access Google Pay transaction data."""
        tokens = self.load_tokens()
        access_token = tokens['access_token']
        
        # Google Pay API for transactions (if available)
        # This requires additional OAuth scopes beyond fitness
        
        # Check available APIs
        req = urllib.request.Request(
            'https://walletobjects.googleapis.com/v1/issuer',
            method='GET'
        )
        req.add_header('Authorization', f'Bearer {access_token}')
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                return {"status": "success", "data": result}
        except urllib.error.HTTPError as e:
            if e.code == 403:
                return {"status": "unauthorized", "error": "Wallet API not enabled or insufficient permissions"}
            return {"status": "error", "code": e.code, "message": e.read().decode()[:200]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_pay_scopes_needed(self):
        """Return the OAuth scopes needed for transaction access."""
        return [
            "https://www.googleapis.com/auth/wallet_object",
            "https://www.googleapis.com/auth/paymentssandbox.make_payments",
            "https://www.googleapis.com/auth/paymentssandbox.read_transaction_info",
        ]
    
    def generate_auth_url(self):
        """Generate OAuth URL for Wallet/Pay permissions."""
        import secrets, hashlib, base64, urllib.parse
        
        # PKCE
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('ascii')
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode('ascii')
        state = base64.urlsafe_b64encode(secrets.token_bytes(16)).rstrip(b'=').decode('ascii')
        
        # Save verifier
        with open('/home/openclaw/.openclaw/workspace/.wallet_oauth', 'w') as f:
            f.write(f'code_verifier={code_verifier}\n')
            f.write(f'state={state}\n')
        
        client_id = '1039635895680-c9sqleuqc9dn46f6t3s1ea1poa82kctt.apps.googleusercontent.com'
        
        scopes = [
            'https://www.googleapis.com/auth/wallet_object',
        ]
        
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'scope': ' '.join(scopes),
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'access_type': 'offline',
            'include_granted_scopes': 'true',
            'prompt': 'consent',
        }
        
        auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params)
        return auth_url
    
    def save_transaction(self, transaction):
        """Save a transaction to local storage."""
        transactions = []
        if self.transactions_file.exists():
            with open(self.transactions_file) as f:
                transactions = json.load(f)
        
        transactions.append({
            **transaction,
            "recorded_at": datetime.utcnow().isoformat()
        })
        
        with open(self.transactions_file, 'w') as f:
            json.dump(transactions, f, indent=2)
    
    def get_transaction_summary(self, days=30):
        """Get summary of recent transactions."""
        if not self.transactions_file.exists():
            return {"error": "No transactions recorded yet"}
        
        with open(self.transactions_file) as f:
            transactions = json.load(f)
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [t for t in transactions if datetime.fromisoformat(t.get('date', '2000-01-01')) > cutoff]
        
        total = sum(t.get('amount', 0) for t in recent)
        by_category = {}
        for t in recent:
            cat = t.get('category', 'Unknown')
            by_category[cat] = by_category.get(cat, 0) + t.get('amount', 0)
        
        return {
            "period_days": days,
            "total_spent": total,
            "transaction_count": len(recent),
            "by_category": by_category,
            "transactions": recent[-10:]  # Last 10
        }

def check_wallet_api_status():
    """Check if Wallet API is accessible with current tokens."""
    tracker = WalletTracker()
    return tracker.check_pay_api_access()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        tracker = WalletTracker()
        url = tracker.generate_auth_url()
        print("Authorization URL:")
        print(url)
    else:
        status = check_wallet_api_status()
        print(json.dumps(status, indent=2))
