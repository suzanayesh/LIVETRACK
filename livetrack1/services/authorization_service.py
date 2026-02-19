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
    # Root-only actions
    # ============================================================

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
    def can_close_ticket(role: str) -> bool:
        return role in ["ROOT", "ADMIN"]

    @staticmethod
    def can_delete_ticket(role: str) -> bool:
        return role == "ROOT"

    # ============================================================
    # Snapshot protection
    # ============================================================

    @staticmethod
    def can_edit_customer_snapshot(role: str) -> bool:
        """
        Snapshot data must NEVER be editable after ticket creation.
        """
        return False

    # ============================================================
    # Status transitions (Lifecycle)
    # ============================================================

    @staticmethod
    def can_change_status(role: str, from_status: str, to_status: str) -> bool:

        # Only Admin or Root can change status
        if role not in ["ROOT", "ADMIN"]:
            return False

        allowed_transitions = {
            "PENDING": ["ACCEPTED"],
            "ACCEPTED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["DONE"],
            "DONE": ["CLOSED"],
        }

    @staticmethod
    def is_root(user):
        return user.role == "ROOT"

    @staticmethod
    def can_manage_distributors(user):
        return user.role == "ROOT"
        # Lifecycle validation
        if to_status not in allowed_transitions.get(from_status, []):
            return False

        # If needed, enforce stricter rule:
        # Uncomment this if ONLY ROOT can close
        # if from_status == "DONE" and to_status == "CLOSED":
        #     return role == "ROOT"

        return True
