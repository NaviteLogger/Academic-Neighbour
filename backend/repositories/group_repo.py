from sqlmodel import Session, desc, select

from models.models import Group, GroupMember, Post, User


def create_group(session: Session, group: Group) -> Group:
    """Create a new group."""
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def get_all_groups(session: Session) -> list[Group]:
    """Get all groups ordered by name."""
    statement = select(Group).order_by(Group.name)
    return list(session.exec(statement).all())


def get_group_by_id(session: Session, group_id: int) -> Group | None:
    """Get a group by ID."""
    return session.get(Group, group_id)


def add_member(session: Session, group_id: int, user_id: int) -> GroupMember:
    """Add a user to a group."""
    member = GroupMember(group_id=group_id, user_id=user_id)
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def remove_member(session: Session, group_id: int, user_id: int) -> bool:
    """Remove a user from a group."""
    member = session.exec(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    ).first()
    if not member:
        return False
    session.delete(member)
    session.commit()
    return True


def is_member(session: Session, group_id: int, user_id: int) -> bool:
    """Check if a user is a member of a group."""
    member = session.exec(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    ).first()
    return member is not None


def get_group_members(session: Session, group_id: int) -> list[User]:
    """Get all members of a group."""
    statement = (
        select(User)
        .join(GroupMember, User.id == GroupMember.user_id)
        .where(GroupMember.group_id == group_id)
    )
    return list(session.exec(statement).all())


def get_group_posts(session: Session, group_id: int) -> list[Post]:
    """Get all posts for a specific group."""
    statement = select(Post).where(Post.group_id == group_id).order_by(desc(Post.created_at))
    return list(session.exec(statement).all())
