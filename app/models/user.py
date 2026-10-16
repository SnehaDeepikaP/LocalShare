from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)  # stores hashed password (or migrated plaintext)
    location = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user', index=True)  # 'user', 'admin'
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_suspended = db.Column(db.Boolean, nullable=False, default=False, index=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    sent_requests = db.relationship('ExchangeRequest', backref='requester', lazy='dynamic', cascade='all, delete-orphan')
    reports_filed = db.relationship('Report', foreign_keys='Report.reporter_id', backref='reporter', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='admin_user', lazy='dynamic')

    @property
    def reputation(self):
        """Calculate member reputation metrics based on genuine completed reviews."""
        reviews = self.reviews_received.all()
        if not reviews:
            return {'average': 5.0, 'count': 0, 'label': 'New Neighbor'}
        avg = round(sum(r.rating for r in reviews) / len(reviews), 1)
        if len(reviews) >= 5 and avg >= 4.5:
            label = 'Trusted Pillar'
        elif len(reviews) >= 2:
            label = 'Active Helper'
        else:
            label = 'Community Member'
        return {'average': avg, 'count': len(reviews), 'label': label}

    @property
    def unread_notifications_count(self):
        return self.notifications.filter_by(is_read=False).count()

    def set_password(self, plaintext_password):
        """Hash and set password using Werkzeug PBKDF2/Scrypt."""
        self.password = generate_password_hash(plaintext_password)

    def check_password(self, candidate_password):
        """
        Verify password against hash.
        Includes backward-compatibility: if existing database record contains
        a legacy plaintext password, it verifies and automatically transparently
        migrates the password to a secure Werkzeug hash upon successful login.
        """
        if not self.password:
            return False

        # Check if password is already a Werkzeug hash (starts with method$ e.g. pbkdf2: or scrypt:)
        if self.password.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
            return check_password_hash(self.password, candidate_password)
        else:
            # Legacy plaintext match check
            if self.password == candidate_password:
                # Transparently upgrade to secure hash!
                self.set_password(candidate_password)
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                return True
            return False

    @property
    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'location': self.location,
            'role': self.role,
            'is_suspended': self.is_suspended,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"
