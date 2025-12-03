"""
Members API router - Member and role management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from api.routers.auth import get_current_user, User

router = APIRouter(tags=["members"])


class RoleInfo(BaseModel):
    id: int
    name: str
    color: str


class MemberItem(BaseModel):
    id: int
    name: str
    display_name: str
    avatar: Optional[str]
    status: str
    roles: List[RoleInfo]


class RoleItem(BaseModel):
    id: int
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
    user_id: int
    role_id: int


class RemoveRoleRequest(BaseModel):
    user_id: int
    role_id: int


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
                            "id": role.id,
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
                    "id": member.id,
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
                    "id": role.id,
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


@router.post("/add_role")
async def add_role(
    request: AddRoleRequest,
    current_user: User = Depends(get_current_user),
):
    """Add a role to a member"""
    try:
        from api.main import bot_instance
        from config.settings import GUILD_ID
        import asyncio

        bot = bot_instance
        if not bot or not bot.is_ready():
            raise HTTPException(status_code=503, detail="Bot is not ready")

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")

        role = guild.get_role(request.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Fetch member asynchronously
        async def add_role_async():
            try:
                member = await guild.fetch_member(request.user_id)
                if not member:
                    return {"success": False, "error": "Member not found"}

                # Check if member already has the role
                if role in member.roles:
                    return {"success": False, "error": "Member already has this role"}

                # Add the role
                await member.add_roles(role)
                return {
                    "success": True,
                    "message": f"Added {role.name} to {member.name}",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Run in bot's event loop
        future = asyncio.run_coroutine_threadsafe(add_role_async(), bot.loop)
        result = future.result(timeout=10)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove_role")
async def remove_role(
    request: RemoveRoleRequest,
    current_user: User = Depends(get_current_user),
):
    """Remove a role from a member"""
    try:
        from api.main import bot_instance
        from config.settings import GUILD_ID
        import asyncio

        bot = bot_instance
        if not bot or not bot.is_ready():
            raise HTTPException(status_code=503, detail="Bot is not ready")

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")

        role = guild.get_role(request.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Fetch member asynchronously
        async def remove_role_async():
            try:
                member = await guild.fetch_member(request.user_id)
                if not member:
                    return {"success": False, "error": "Member not found"}

                # Check if member does not have the role
                if role not in member.roles:
                    return {"success": False, "error": "Member does not have this role"}

                # Remove the role
                await member.remove_roles(role)
                return {
                    "success": True,
                    "message": f"Removed {role.name} from {member.name}",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Run in bot's event loop
        future = asyncio.run_coroutine_threadsafe(remove_role_async(), bot.loop)
        result = future.result(timeout=10)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
