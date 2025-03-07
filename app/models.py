from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """사용자 모델 (추후 OAuth 로그인에 활용 가능)"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"
