import bcrypt
import logging

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        logging.basicConfig(filename='user.log', level=logging.INFO, format='%(asctime)s %(message)s')

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def __repr__(self):
        return f"User(username={self.username}, role={self.role})"

    @staticmethod
    def validate_role(role):
        """Validate the user role."""
        if role not in ["admin", "trader", "viewer"]:
            logging.error(f"Invalid role: {role}")
            raise ValueError("Role must be either 'admin', 'trader', or 'viewer'")
        return True

    def change_password(self, old_password, new_password):
        """Change the user's password if the old password matches."""
        if self.check_password(old_password):
            self.password = self.hash_password(new_password)
            logging.info(f"Password changed for user: {self.username}")
        else:
            logging.warning(f"Failed password change attempt for user: {self.username}")
            raise ValueError("Old password does not match")

    def set_role(self, new_role):
        """Set a new role for the user."""
        self.validate_role(new_role)
        self.role = new_role
        logging.info(f"Role changed to {new_role} for user: {self.username}")
