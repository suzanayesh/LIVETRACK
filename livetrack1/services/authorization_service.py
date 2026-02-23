class AuthorizationService:
    """
    Central place for role-based authorization rules.
    """

    # ============================================================
    # Role checks
    # ============================================================

    @staticmethod
    def is_root(role: str) -> bool:
        return role == "ROOT"

    @staticmethod
    def is_admin(role: str) -> bool:
        return role == "ADMIN"

    # ============================================================
    # Admin management
    # ============================================================

    @staticmethod
    def can_manage_admins(role: str) -> bool:
        return role == "ROOT"

    @staticmethod
    def can_create_admin(role: str) -> bool:
        return role == "ROOT"

    @staticmethod
    def can_delete_admin(role: str) -> bool:
        return role == "ROOT"

    # ============================================================
    # Ticket permissions
    # ============================================================

    @staticmethod
    def can_create_ticket(role: str) -> bool:
        return role in ["ROOT", "ADMIN"]

    @staticmethod
    def can_assign_ticket(role: str) -> bool:
        return role in ["ROOT", "ADMIN"]

    @staticmethod
    def can_delete_ticket(role: str) -> bool:
        return role == "ROOT"

    # ============================================================
    # Lifecycle
    # ============================================================

    @staticmethod
    def can_change_status(role: str, from_status: str, to_status: str) -> bool:

        if role not in ["ROOT", "ADMIN"]:
            return False

        allowed_transitions = {
            "PENDING": ["ACCEPTED"],
            "ACCEPTED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["DONE"],
            "DONE": ["CLOSED"],
        }

        if to_status not in allowed_transitions.get(from_status, []):
            return False

        return True
