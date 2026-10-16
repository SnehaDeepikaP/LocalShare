import os
from flask import Flask, render_template
from app.config import config_by_name
from app.extensions import db, migrate
from app.services.security_service import generate_csrf_token, add_security_headers

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register context processors
    @app.context_processor
    def inject_global_data():
        unread = 0
        from flask import session
        if 'user_id' in session:
            try:
                from app.models.notification import Notification
                unread = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
            except Exception:
                unread = 0
        return dict(csrf_token=generate_csrf_token, unread_notifications_count=unread)

    # Register after-request security headers
    app.after_request(add_security_headers)

    # Register Blueprints
    from app.auth import auth_bp
    from app.posts import posts_bp
    from app.exchange import exchange_bp
    from app.matching.routes import matching_bp
    from app.admin import admin_bp
    from app.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(exchange_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    # Register Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # CLI commands for easy database setup and administration
    register_cli_commands(app)

    return app


def register_cli_commands(app):
    @app.cli.command('init-db')
    def init_db_cmd():
        """Create tables and run schema upgrades."""
        with app.app_context():
            db.create_all()
            from app.models.user import User
            from app.models.post import Post
            # Ensure admin exists
            admin = User.query.filter_by(email='admin@localshare.dev').first()
            if not admin:
                admin = User(
                    name='Platform Administrator',
                    email='admin@localshare.dev',
                    location='Hyderabad',
                    role='admin',
                    is_active=True,
                    is_suspended=False
                )
                admin.set_password('Admin@123')
                db.session.add(admin)
                db.session.commit()
                print("Default admin created: admin@localshare.dev / Admin@123")
            print("Database initialized successfully.")

    @app.cli.command('seed-demo')
    def seed_demo_cmd():
        """Seed demo community data with secure password hashes."""
        with app.app_context():
            from app.models.user import User
            from app.models.post import Post
            db.create_all()

            # Seed demo users if missing
            users_data = [
                ('Priya Sharma', 'priya@example.com', 'Test@123', 'Hyderabad', 'user'),
                ('Rahul Verma', 'rahul@example.com', 'Test@123', 'Hyderabad', 'user'),
                ('Admin User', 'admin@localshare.dev', 'Admin@123', 'Hyderabad', 'admin'),
            ]
            for name, email, pwd, loc, role in users_data:
                if not User.query.filter_by(email=email).first():
                    u = User(name=name, email=email, location=loc, role=role)
                    u.set_password(pwd)
                    db.session.add(u)
            db.session.commit()

            # Seed demo posts
            posts_data = [
                (1, 'Priya Sharma', 'offer', 'Food',
                 'Home cooked meals on weekends',
                 'I cook extra food every weekend and happy to share. Vegetarian only.',
                 'Hyderabad'),
                (2, 'Rahul Verma', 'request', 'Books',
                 'Need CBSE Class 10 textbooks',
                 'Looking for Science and Maths books for my younger sibling. Any edition works.',
                 'Hyderabad'),
                (1, 'Priya Sharma', 'offer', 'Clothes',
                 'Kids clothes (2–5 years), free to take',
                 'My child has outgrown these. Good condition, free for anyone who needs them.',
                 'Hyderabad'),
                (2, 'Rahul Verma', 'offer', 'Books',
                 'CBSE Class 10 Reference Guides to share',
                 'Finished 10th grade exams, offering Maths and Science reference guides for students.',
                 'Hyderabad'),
            ]
            for u_id, u_name, p_type, cat, title, desc, loc in posts_data:
                existing = Post.query.filter_by(title=title).first()
                if not existing:
                    p = Post(
                        user_id=u_id,
                        user_name=u_name,
                        post_type=p_type,
                        category=cat,
                        title=title,
                        description=desc,
                        location=loc,
                        status='open'
                    )
                    db.session.add(p)
            db.session.commit()
            print("Demo data seeded successfully.")
