from datetime import datetime, timezone
from app.extensions import db

VALID_CATEGORIES = ['Food', 'Clothes', 'Books', 'Services', 'Other']
VALID_TYPES = ['request', 'offer']
VALID_STATUSES = ['open', 'in_progress', 'completed', 'closed']

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    user_name = db.Column(db.String(100), nullable=False)
    post_type = db.Column(db.String(10), nullable=False, index=True)  # 'request' or 'offer'
    category = db.Column(db.String(50), nullable=False, index=True)   # Food, Clothes, Books, Services, Other
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='open', index=True)  # open, in_progress, completed, closed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    exchange_requests = db.relationship('ExchangeRequest', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_open(self):
        return self.status == 'open'

    @property
    def is_offer(self):
        return self.post_type == 'offer'

    @property
    def is_request(self):
        return self.post_type == 'request'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'post_type': self.post_type,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Post id={self.id} type='{self.post_type}' category='{self.category}' status='{self.status}'>"
