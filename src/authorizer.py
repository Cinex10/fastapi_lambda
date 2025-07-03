"""
Lambda Authorizer pour validation JWT avec scopes
Vérifie les JWT tokens et les scopes requis pour l'API Gateway
"""

import json
import os
import logging
from typing import Dict, Any, Optional
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

# Configuration du logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

# Configuration JWT
JWT_SECRET = os.getenv('JWT_SECRET', '###')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')


class AuthorizerError(Exception):
    """Exception personnalisée pour les erreurs d'autorisation"""
    pass


def validate_jwt_token(token: str) -> Dict[str, Any]:
    """
    Valide le token JWT et retourne les claims
    """
    try:
        # Valider et décoder le token
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        logger.info(f"JWT validation successful for subject: {payload.get('sub', 'unknown')}")
        return payload
        
    except ExpiredSignatureError:
        logger.warning("JWT token has expired")
        raise AuthorizerError("Token has expired")
    except InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise AuthorizerError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise AuthorizerError(f"Token validation failed: {str(e)}")


def check_required_scope(claims: Dict[str, Any], required_scope: str) -> bool:
    """
    Vérifie si le token contient le scope requis
    """
    # Les scopes peuvent être dans 'scope' (string séparé par espaces) ou 'scopes' (array)
    token_scopes = []
    
    if 'scopes' in claims:
        token_scopes = claims['scopes'].split()
    
    logger.info(f"Token scopes: {token_scopes}, Required scope: {required_scope}")
    
    return required_scope in token_scopes


def extract_token_from_header(auth_header: str) -> str:
    """
    Extrait le token JWT du header Authorization
    """
    if not auth_header:
        raise AuthorizerError("Missing Authorization header")
    
    if not auth_header.startswith('Bearer '):
        raise AuthorizerError("Authorization header must start with 'Bearer '")
    
    return auth_header[7:]  # Enlever 'Bearer '


def determine_required_scope(method_arn: str) -> Optional[str]:
    """
    Détermine le scope requis basé sur l'ARN de la méthode
    """
    # Exemple d'ARN: arn:aws:execute-api:region:account:api-id/stage/method/resource
    arn_parts = method_arn.split('/')
    
    if len(arn_parts) < 3:
        return None
    
    method = arn_parts[2]  # GET, POST, etc.
    resource = '/'.join(arn_parts[3:]) if len(arn_parts) > 3 else ''
    
    logger.info(f"Determining scope for method: {method}, resource: {resource}")
    
    # Règles de mapping méthode/ressource -> scope
    if method == 'POST' and 'orders' in resource:
        return 'orders:write'
    elif method == 'PUT' and 'orders' in resource:
        return 'orders:write'
    elif method == 'DELETE' and 'orders' in resource:
        return 'orders:delete'
    elif method == 'GET' and 'orders' in resource:
        return 'orders:read'
    
    return None


def generate_policy(principal_id: str, effect: str, resource: str) -> Dict[str, Any]:
    """
    Génère la politique d'autorisation pour API Gateway
    """
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }
    

    
    return policy


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal du Lambda Authorizer
    """
    try:
        logger.info(f"Authorizer invoked with event: {json.dumps(event, default=str)}")
        
        # Extraire les informations de l'événement
        token = extract_token_from_header(event.get('authorizationToken', ''))
        method_arn = event.get('methodArn', '')
        
        # Valider le token JWT
        claims = validate_jwt_token(token)
        
        # Déterminer le scope requis
        required_scope = determine_required_scope(method_arn)
        
        if required_scope:
            # Vérifier le scope
            if not check_required_scope(claims, required_scope):
                logger.warning(f"Insufficient scope. Required: {required_scope}")
                raise AuthorizerError(f"Insufficient scope: {required_scope} required")
        

        
        # Générer la politique d'autorisation
        policy = generate_policy(
            principal_id=claims.get('sub', 'user'),
            effect='Allow',
            resource=method_arn
        )
        
        logger.info(f"Authorization successful for user: {claims.get('sub', 'unknown')}")
        return policy
        
    except AuthorizerError as e:
        logger.warning(f"Authorization failed: {str(e)}")
        # Retourner une politique de refus
        return generate_policy(
            principal_id='user',
            effect='Deny',
            resource=event.get('methodArn', '*')
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in authorizer: {str(e)}")
        # En cas d'erreur inattendue, refuser l'accès
        return generate_policy(
            principal_id='user',
            effect='Deny',
            resource=event.get('methodArn', '*')
        )


# Pour les tests locaux
if __name__ == "__main__":
    # Exemple d'événement de test
    test_event = {
        "authorizationToken": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
        "methodArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef123/test/POST/orders"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2)) 