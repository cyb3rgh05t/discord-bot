"""
Members API router - Member and role management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from typing import Optional, List
from pydantic import BaseModel
from api.routers.auth import (
    get_current_user,
    get_current_user_manual,
    verify_token_header,
    User,
)

router = APIRouter(tags=["members"])


class RoleInfo(BaseModel):
    id: str
    name: str
    color: str


class MemberItem(BaseModel):
    id: str
    name: str
    display_name: str
    avatar: Optional[str]
    status: str
    roles: List[RoleInfo]


class RoleItem(BaseModel):
    id: str
    name: str
    color: str
    position: int
    mentionable: bool
    hoist: bool
    member_count: int


class MembersStats(BaseModel):
    total_members: int
    total_roles: int


class MembersResponse(BaseModel):
    members: List[MemberItem]
    roles: List[RoleItem]
    stats: MembersStats
    total_pages: int


class AddRoleRequest(BaseModel):
    user_id: str
    role_id: str


class RemoveRoleRequest(BaseModel):
    user_id: str
    role_id: str


# Helper functions for bot interaction
async def bot_add_role_to_member(user_id: str, role_id: str) -> dict:
    """Add a role to a member using the bot instance"""
    from api.main import bot_instance
    from config.settings import GUILD_ID
    import asyncio

    print(f"[DEBUG] bot_add_role_to_member: user_id={user_id}, role_id={role_id}")

    bot = bot_instance
    print(f"[DEBUG] bot_instance: {bot}, is_ready: {bot.is_ready() if bot else 'N/A'}")
    if not bot or not bot.is_ready():
        return {"success": False, "error": "Bot is not ready"}

    guild = bot.get_guild(int(GUILD_ID))
    print(f"[DEBUG] GUILD_ID: {GUILD_ID}, guild: {guild}")
    if not guild:
        return {"success": False, "error": "Guild not found"}

    role = guild.get_role(int(role_id))
    print(f"[DEBUG] Looking for role_id={role_id}, found: {role}")
    if not role:
        return {"success": False, "error": "Role not found"}

    try:
        member = await guild.fetch_member(int(user_id))
        print(f"[DEBUG] Looking for user_id={user_id}, found: {member}")
        if not member:
            return {"success": False, "error": "Member not found"}

        print(f"[DEBUG] Member roles: {[r.id for r in member.roles]}")
        if role in member.roles:
            return {"success": False, "error": "Member already has this role"}

        await member.add_roles(role)
        print(f"[DEBUG] Successfully added role {role.name} to {member.name}")
        return {"success": True, "message": f"Added {role.name} to {member.name}"}
    except Exception as e:
        print(f"[DEBUG] Exception in bot_add_role_to_member: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def bot_remove_role_from_member(user_id: str, role_id: str) -> dict:
    """Remove a role from a member using the bot instance"""
    from api.main import bot_instance
    from config.settings import GUILD_ID
    import asyncio

    print(f"[DEBUG] bot_remove_role_from_member: user_id={user_id}, role_id={role_id}")

    bot = bot_instance
    print(f"[DEBUG] bot_instance: {bot}, is_ready: {bot.is_ready() if bot else 'N/A'}")
    if not bot or not bot.is_ready():
        return {"success": False, "error": "Bot is not ready"}

    guild = bot.get_guild(int(GUILD_ID))
    print(f"[DEBUG] GUILD_ID: {GUILD_ID}, guild: {guild}")
    if not guild:
        return {"success": False, "error": "Guild not found"}

    role = guild.get_role(int(role_id))
    print(f"[DEBUG] Looking for role_id={role_id}, found: {role}")
    if not role:
        return {"success": False, "error": "Role not found"}

    try:
        member = await guild.fetch_member(int(user_id))
        print(f"[DEBUG] Looking for user_id={user_id}, found: {member}")
        if not member:
            return {"success": False, "error": "Member not found"}

        print(f"[DEBUG] Member roles: {[r.id for r in member.roles]}")
        if role not in member.roles:
            return {"success": False, "error": "Member does not have this role"}

        await member.remove_roles(role)
        print(f"[DEBUG] Successfully removed role {role.name} from {member.name}")
        return {"success": True, "message": f"Removed {role.name} from {member.name}"}
    except Exception as e:
        print(f"[DEBUG] Exception in bot_remove_role_from_member: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


@router.post("/test_endpoint")
async def test_endpoint(data: dict):
    """Test endpoint to verify POST requests work"""
    return {"success": True, "received": data}


@router.post("/test_with_model")
async def test_with_model(request: AddRoleRequest):
    """Test endpoint with Pydantic model but no auth"""
    return {"success": True, "user_id": request.user_id, "role_id": request.role_id}


@router.post("/test_with_header_auth")
async def test_with_header_auth(current_user: User = Depends(verify_token_header)):
    """Test endpoint with ONLY Header auth dependency, no Pydantic model"""
    return {"success": True, "user": current_user.username}


@router.post("/test_full_combo")
async def test_full_combo(request: Request, body: AddRoleRequest):
    """Test endpoint with Request + Pydantic model + manual auth (like add_role)"""
    current_user = await verify_token_header(request.headers.get("authorization"))
    return {
        "success": True,
        "user": current_user.username,
        "user_id": body.user_id,
        "role_id": body.role_id,
    }


def get_guild_members_from_bot():
    """Get guild members from bot instance"""
    try:
        from api.main import bot_instance
        from config.settings import GUILD_ID

        bot = bot_instance
        if not bot or not bot.is_ready():
            return []

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            return []

        members = []
        for member in guild.members:
            # Skip bots
            if member.bot:
                continue

            # Get member status
            status = str(member.status)

            # Get member roles (excluding @everyone)
            roles = []
            for role in member.roles:
                if role.name != "@everyone":
                    roles.append(
                        {
                            "id": str(role.id),
                            "name": role.name,
                            "color": (
                                f"#{role.color.value:06x}"
                                if role.color.value
                                else "#99aab5"
                            ),
                        }
                    )

            members.append(
                {
                    "id": str(member.id),
                    "name": str(member),
                    "display_name": member.display_name,
                    "avatar": (
                        str(member.display_avatar.url)
                        if member.display_avatar
                        else None
                    ),
                    "status": status,
                    "roles": roles,
                }
            )

        return members
    except Exception as e:
        print(f"Error getting guild members: {e}")
        return []


def get_guild_roles_from_bot():
    """Get guild roles from bot instance"""
    try:
        from api.main import bot_instance
        from config.settings import GUILD_ID

        bot = bot_instance
        if not bot or not bot.is_ready():
            return []

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            return []

        roles = []
        for role in guild.roles:
            # Skip @everyone role
            if role.name == "@everyone":
                continue

            # Count members with this role
            member_count = sum(1 for member in guild.members if role in member.roles)

            roles.append(
                {
                    "id": str(role.id),
                    "name": role.name,
                    "color": (
                        f"#{role.color.value:06x}" if role.color.value else "#99aab5"
                    ),
                    "position": role.position,
                    "mentionable": role.mentionable,
                    "hoist": role.hoist,
                    "member_count": member_count,
                }
            )

        # Sort by position (highest first)
        roles.sort(key=lambda x: x["position"], reverse=True)

        return roles
    except Exception as e:
        print(f"Error getting guild roles: {e}")
        return []


@router.get("/", response_model=MembersResponse)
async def get_members(
    page: int = Query(1),
    per_page: int = Query(10),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get all members and roles with filtering and pagination"""
    try:
        members = get_guild_members_from_bot()
        roles = get_guild_roles_from_bot()

        # Filter by search if provided
        if search:
            search_lower = search.lower()
            members = [
                m
                for m in members
                if search_lower in m.get("name", "").lower()
                or search_lower in str(m.get("id", "")).lower()
            ]

        # Calculate pagination for members
        total_members = len(members)
        total_pages = (
            (total_members + per_page - 1) // per_page if total_members > 0 else 0
        )
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_members = members[start_idx:end_idx]

        return MembersResponse(
            members=[MemberItem(**m) for m in paginated_members],
            roles=[RoleItem(**r) for r in roles],
            stats=MembersStats(
                total_members=total_members,
                total_roles=len(roles),
            ),
            total_pages=total_pages,
        )

    except Exception as e:
        print(f"Error fetching members: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/member/add-role")
async def add_role(body: AddRoleRequest, authorization: str = Header(None)):
    """Add a role to a member"""
    current_user = await verify_token_header(authorization)
    print(
        f"[DEBUG] add_role endpoint called: user_id={body.user_id}, role_id={body.role_id}"
    )

    from api.main import bot_instance
    import asyncio

    # Run the helper function in the bot's event loop
    try:
        future = asyncio.run_coroutine_threadsafe(
            bot_add_role_to_member(body.user_id, body.role_id), bot_instance.loop
        )
        result = future.result(timeout=10)
        print(f"[DEBUG] add_role result: {result}")

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/member/remove-role")
async def remove_role(body: RemoveRoleRequest, authorization: str = Header(None)):
    """Remove a role from a member"""
    current_user = await verify_token_header(authorization)
    print(
        f"[DEBUG] remove_role endpoint called: user_id={body.user_id}, role_id={body.role_id}"
    )

    from api.main import bot_instance
    import asyncio

    # Run the helper function in the bot's event loop
    try:
        future = asyncio.run_coroutine_threadsafe(
            bot_remove_role_from_member(body.user_id, body.role_id), bot_instance.loop
        )
        result = future.result(timeout=10)
        print(f"[DEBUG] remove_role result: {result}")

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
