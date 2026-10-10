from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.database import get_session
from models.models import (
    Group,
    GroupCreate,
    GroupRead,
    Post,
    PostCreate,
    PostWithAuthor,
    User,
)
from repositories.group_repo import (
    add_member,
    create_group,
    get_all_groups,
    get_group_by_id,
    get_group_members,
    get_group_posts,
    is_member,
    remove_member,
)
from repositories.post_repo import create_post
from services.security import get_current_active_user

router = APIRouter(prefix="/groups", tags=["groups"])

session: Session = Depends(get_session)
current_user: User = Depends(get_current_active_user)


@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group_endpoint(
    group_data: GroupCreate,
    current_user: User = current_user,
    session: Session = session,
) -> Group:
    """Create a new group."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    group = Group(
        name=group_data.name,
        description=group_data.description,
        creator_id=current_user.id,
    )
    created_group = create_group(session, group)

    # Creator automatically joins the group
    if created_group.id:
        add_member(session, created_group.id, current_user.id)

    return created_group


@router.get("/", response_model=list[GroupRead])
def get_groups(session: Session = session) -> list[Group]:
    """List all groups."""
    return get_all_groups(session)


@router.get("/{group_id}", response_model=GroupRead)
def get_group(
    group_id: int,
    session: Session = session,
) -> Group:
    """Get group details."""
    group = get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@router.post("/{group_id}/join", status_code=status.HTTP_200_OK)
def join_group(
    group_id: int,
    current_user: User = current_user,
    session: Session = session,
):
    """Join a group."""
    group = get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    if is_member(session, group_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of this group"
        )

    add_member(session, group_id, current_user.id)
    return {"message": "Successfully joined the group"}


@router.post("/{group_id}/leave", status_code=status.HTTP_200_OK)
def leave_group(
    group_id: int,
    current_user: User = current_user,
    session: Session = session,
):
    """Leave a group."""
    group = get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    if not is_member(session, group_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not a member of this group"
        )

    remove_member(session, group_id, current_user.id)
    return {"message": "Successfully left the group"}


@router.get("/{group_id}/members", response_model=list[User])
def get_members(
    group_id: int,
    session: Session = session,
) -> list[User]:
    """List group members."""
    group = get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    return get_group_members(session, group_id)


@router.post(
    "/{group_id}/posts", response_model=PostWithAuthor, status_code=status.HTTP_201_CREATED
)
def create_group_post(
    group_id: int,
    post_data: PostCreate,
    current_user: User = current_user,
    session: Session = session,
) -> PostWithAuthor:
    """Create a post within a group."""
    group = get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    if not is_member(session, group_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Must be a member to post in this group"
        )

    post = Post(
        content=post_data.content,
        author_id=current_user.id,
        group_id=group_id,
    )
    created_post = create_post(session, post)

    if not created_post.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Post creation failed"
        )

    return PostWithAuthor(
        id=created_post.id,
        content=created_post.content,
        author_id=created_post.author_id,
        created_at=str(created_post.created_at),
        author_name=current_user.username,
    )


@router.get("/{group_id}/posts", response_model=list[PostWithAuthor])
def get_group_posts_endpoint(
    group_id: int,
    session: Session = session,
) -> list[PostWithAuthor]:
    """Get posts for a specific group."""
    group = get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    posts = get_group_posts(session, group_id)

    # We need to fetch author names efficiently, but for now we'll do it simply
    # In a real app, we'd use a join in the repo
    result: list[PostWithAuthor] = []
    for post in posts:
        if not post.id:
            continue
        author = session.get(User, post.author_id)
        author_name = author.username if author else "Unknown"

        result.append(
            PostWithAuthor(
                id=post.id,
                content=post.content,
                author_id=post.author_id,
                created_at=str(post.created_at),
                author_name=author_name,
            )
        )
    return result
