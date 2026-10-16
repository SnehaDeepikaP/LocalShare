from datetime import datetime, timezone
from app.extensions import db

class SavedListing(db.Model):
    __tablename__ = 'saved_listings'
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_saved_post'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship('User', backref=db.backref('saved_posts', lazy='dynamic', cascade='all, delete-orphan'))
    post = db.relationship('Post', backref=db.backref('saved_by_users', lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<SavedListing user_id={self.user_id} post_id={self.post_id}>"
