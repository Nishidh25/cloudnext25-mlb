"""Create, delete and update records with SQLAlchemy's ORM."""
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import Column, DateTime, Integer, String, Text,Boolean
from sqlalchemy.sql import text
from database.model import UserProfile


# 1. Adding/Creating a User
def orm_create_user(session: Session, email: str, first_name: str, last_name: str) -> UserProfile:
    """
    Create a new user in the database with the given email, first name, and last name.

    :param Session session: SQLAlchemy database session.
    :param str email: The user's email.
    :param str first_name: The user's first name.
    :param str last_name: The user's last name.
    :return: UserProfile object created.
    """
    try:
        user = UserProfile(email=email, first_name=first_name, last_name=last_name)
        session.add(user)  # Add the user to the session
        session.commit()  # Commit the change to the database
        return user
    except SQLAlchemyError as e:
        session.rollback()  # Rollback in case of error
        print(f"Error creating user: {e}")
        return None
# 2. Subscribing a User by email (Create if not exists, or Update if exists)
def orm_subscribe_user(session: Session, email: str, first_name: str, last_name: str, team: str, player: str) -> bool:
    """
    Subscribe a user (set is_subscribed to 1) by the given email, and create a new user if the email does not exist.

    :param Session session: SQLAlchemy database session.
    :param str email: The user's email to update subscription status or create the user.
    :param str first_name: The user's first name.
    :param str last_name: The user's last name.
    :param str team: The user's team.
    :param str player: The user's player role.
    :return: True if successful, False otherwise.
    """
    try:
        # If the user doesn't exist, create a new one
            new_subscription = UserProfile(
                email=email,
                first_name=first_name,
                last_name=last_name,
                team=team,
                player=player,
                is_subscribed=1 # Set is_subscribed to 1 (subscribed)
            )
            session.add(new_subscription)  # Add the new user to the session
            session.commit()  # Commit the change to the database
            return True
    except SQLAlchemyError as e:
        session.rollback()  # Rollback in case of error
        print(f"Error subscribing user: {e}")
        return False

# 3. Unsubscribing a User
def orm_unsubscribe_user(session: Session, user_id: int) -> bool:
    """
    Update the user to be unsubscribed (set is_subscribed to 0) for the given user id.

    :param Session session: SQLAlchemy database session.
    :param int user_id: The user's ID to update subscription status.
    :return: True if successful, False otherwise.
    """
    try:
        user = session.query(UserProfile).filter_by(id=user_id).first()  # Get user by ID
        if user:
            user.is_subscribed = 0  # Set is_subscribed to 0 (unsubscribed)
            session.commit()  # Commit the change to the database
            return True
        else:
            print(f"User with id {user_id} not found.")
            return False
    except SQLAlchemyError as e:
        session.rollback()  # Rollback in case of error
        print(f"Error unsubscribing user: {e}")
        return False

# 4. Fetching Users by Email with Subscription Status
def orm_get_user_by_email(session: Session, email: str) -> list:
    """
    Fetch all user profiles by email and their subscription status (is_subscribed).

    :param Session session: SQLAlchemy database session.
    :param str email: The email to search for users.
    :return: List of UserProfile objects.
    """
    try:
        users = session.query(UserProfile).filter_by(email=email).all()  # Get users by email
        return users
    except SQLAlchemyError as e:
        print(f"Error fetching user by email: {e}")
        return []