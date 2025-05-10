from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from typing import Generator, Optional
from .models import Base

# Configure logging
logger = logging.getLogger(__name__)

class Database:
    """Database connection and session management."""
    
    def __init__(self, database_url: str):
        """Initialize database connection.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False
        )
        self.SessionFactory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )
        self.Session = scoped_session(self.SessionFactory)

    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator:
        """Get a database session.
        
        Yields:
            SQLAlchemy session
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: User's Telegram ID
            
        Returns:
            User data dictionary or None if not found
        """
        try:
            with self.get_session() as session:
                user = session.query(Base.metadata.tables['users']).filter_by(
                    telegram_id=telegram_id
                ).first()
                return dict(user) if user else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by Telegram ID: {e}")
            return None

    def create_user(self, user_data: dict) -> Optional[dict]:
        """Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Created user data dictionary or None if failed
        """
        try:
            with self.get_session() as session:
                user = Base.metadata.tables['users'](**user_data)
                session.add(user)
                session.flush()
                return dict(user)
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            return None

    def update_user(self, telegram_id: int, user_data: dict) -> bool:
        """Update user data.
        
        Args:
            telegram_id: User's Telegram ID
            user_data: Updated user data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.query(Base.metadata.tables['users']).filter_by(
                    telegram_id=telegram_id
                ).update(user_data)
                return bool(result)
        except SQLAlchemyError as e:
            logger.error(f"Error updating user: {e}")
            return False

    def delete_user(self, telegram_id: int) -> bool:
        """Delete user.
        
        Args:
            telegram_id: User's Telegram ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.query(Base.metadata.tables['users']).filter_by(
                    telegram_id=telegram_id
                ).delete()
                return bool(result)
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user: {e}")
            return False

    def get_matches(self, user_id: int, status: str = None) -> list:
        """Get user matches.
        
        Args:
            user_id: User ID
            status: Match status filter
            
        Returns:
            List of matches
        """
        try:
            with self.get_session() as session:
                query = session.query(Base.metadata.tables['matches']).filter_by(
                    user_id=user_id
                )
                if status:
                    query = query.filter_by(status=status)
                return [dict(match) for match in query.all()]
        except SQLAlchemyError as e:
            logger.error(f"Error getting matches: {e}")
            return []

    def create_match(self, match_data: dict) -> Optional[dict]:
        """Create a new match.
        
        Args:
            match_data: Match data dictionary
            
        Returns:
            Created match data dictionary or None if failed
        """
        try:
            with self.get_session() as session:
                match = Base.metadata.tables['matches'](**match_data)
                session.add(match)
                session.flush()
                return dict(match)
        except SQLAlchemyError as e:
            logger.error(f"Error creating match: {e}")
            return None

    def update_match(self, match_id: int, match_data: dict) -> bool:
        """Update match data.
        
        Args:
            match_id: Match ID
            match_data: Updated match data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.query(Base.metadata.tables['matches']).filter_by(
                    id=match_id
                ).update(match_data)
                return bool(result)
        except SQLAlchemyError as e:
            logger.error(f"Error updating match: {e}")
            return False

    def get_confessions(self, user_id: int = None, status: str = None) -> list:
        """Get confessions.
        
        Args:
            user_id: User ID filter
            status: Confession status filter
            
        Returns:
            List of confessions
        """
        try:
            with self.get_session() as session:
                query = session.query(Base.metadata.tables['confessions'])
                if user_id:
                    query = query.filter_by(user_id=user_id)
                if status:
                    query = query.filter_by(status=status)
                return [dict(confession) for confession in query.all()]
        except SQLAlchemyError as e:
            logger.error(f"Error getting confessions: {e}")
            return []

    def create_confession(self, confession_data: dict) -> Optional[dict]:
        """Create a new confession.
        
        Args:
            confession_data: Confession data dictionary
            
        Returns:
            Created confession data dictionary or None if failed
        """
        try:
            with self.get_session() as session:
                confession = Base.metadata.tables['confessions'](**confession_data)
                session.add(confession)
                session.flush()
                return dict(confession)
        except SQLAlchemyError as e:
            logger.error(f"Error creating confession: {e}")
            return None

    def update_confession(self, confession_id: int, confession_data: dict) -> bool:
        """Update confession data.
        
        Args:
            confession_id: Confession ID
            confession_data: Updated confession data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.query(Base.metadata.tables['confessions']).filter_by(
                    id=confession_id
                ).update(confession_data)
                return bool(result)
        except SQLAlchemyError as e:
            logger.error(f"Error updating confession: {e}")
            return False

    def get_reports(self, reporter_id: int = None, reported_user_id: int = None, status: str = None) -> list:
        """Get reports.
        
        Args:
            reporter_id: Reporter ID filter
            reported_user_id: Reported user ID filter
            status: Report status filter
            
        Returns:
            List of reports
        """
        try:
            with self.get_session() as session:
                query = session.query(Base.metadata.tables['reports'])
                if reporter_id:
                    query = query.filter_by(reporter_id=reporter_id)
                if reported_user_id:
                    query = query.filter_by(reported_user_id=reported_user_id)
                if status:
                    query = query.filter_by(status=status)
                return [dict(report) for report in query.all()]
        except SQLAlchemyError as e:
            logger.error(f"Error getting reports: {e}")
            return []

    def create_report(self, report_data: dict) -> Optional[dict]:
        """Create a new report.
        
        Args:
            report_data: Report data dictionary
            
        Returns:
            Created report data dictionary or None if failed
        """
        try:
            with self.get_session() as session:
                report = Base.metadata.tables['reports'](**report_data)
                session.add(report)
                session.flush()
                return dict(report)
        except SQLAlchemyError as e:
            logger.error(f"Error creating report: {e}")
            return None

    def update_report(self, report_id: int, report_data: dict) -> bool:
        """Update report data.
        
        Args:
            report_id: Report ID
            report_data: Updated report data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.query(Base.metadata.tables['reports']).filter_by(
                    id=report_id
                ).update(report_data)
                return bool(result)
        except SQLAlchemyError as e:
            logger.error(f"Error updating report: {e}")
            return False 