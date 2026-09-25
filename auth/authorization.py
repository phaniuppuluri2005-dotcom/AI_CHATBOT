"""
Authorization & Data Isolation Module for Phani AI Platform.
Enforces Role-Based Access Control (USER vs ADMIN) and verifies server-side resource ownership.
"""

import logging
from typing import Dict, Any, Optional
from auth.authentication import get_current_user_dict

logger = logging.getLogger("PhaniAI.Authorization")


def is_admin(user: Optional[Dict[str, Any]] = None) -> bool:
    """Check if the current user has ADMIN role privileges."""
    u = user or get_current_user_dict()
    return u.get("role") == "admin"


def verify_resource_ownership(resource_user_id: Optional[int], current_user_id: Optional[int] = None) -> bool:
    """
    Verify server-side resource ownership to prevent horizontal privilege escalation.
    Allows access if resource belongs to current user or if current user is an admin.
    """
    if current_user_id is None:
        user = get_current_user_dict()
        current_user_id = user.get("id")
        if is_admin(user):
            return True

    if resource_user_id is None or current_user_id is None:
        return True

    return resource_user_id == current_user_id
