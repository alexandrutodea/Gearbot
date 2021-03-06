from discord.ext import commands

from Util import Configuration


def is_owner():
    async def predicate(ctx):
        return ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)


def is_trusted(ctx):
    return is_user("TRUSTED", ctx) or is_mod(ctx)

def is_mod(ctx:commands.Context):
    return is_user("MOD", ctx) or (hasattr(ctx.author, "roles") and ctx.channel.permissions_for(ctx.author).ban_members) or is_admin(ctx)

def is_admin(ctx:commands.Context):
    return is_user("ADMIN", ctx) or (hasattr(ctx.author, "roles") and ctx.channel.permissions_for(ctx.author).administrator)

def is_server_owner(ctx):
    return ctx.guild is not None and ctx.author == ctx.guild.owner


def is_user(perm_type, ctx):
    if ctx.guild is None:
        return False
    if not hasattr(ctx.author, "roles"):
        return False
    roles = Configuration.getConfigVar(ctx.guild.id, f"{perm_type}_ROLES")
    for role in ctx.author.roles:
        if role.id in roles:
            return True
    return False

def mod_only():
    async def predicate(ctx):
        return is_mod(ctx)
    return commands.check(predicate)

def is_dev(ctx:commands.Context):
    if ctx.guild is None:
        return False
    devrole = Configuration.getConfigVar(ctx.guild.id, "DEV_ROLE")
    if devrole != 0:
        for role in ctx.author.roles:
            if role.id == devrole:
                return True
    return is_admin(ctx)

def devOnly():
    async def predicate(ctx):
        return is_dev(ctx)
    return commands.check(predicate)

def is_server(ctx, id):
    return ctx.guild is not None and ctx.guild.id == id

def bc_only():
    async def predicate(ctx):
        return is_server(ctx, 309218657798455298)
    return commands.check(predicate)

def no_testers():
    async def predicate(ctx):
        return not is_server(ctx, 197038439483310086)
    return commands.check(predicate)

def check_permission(ctx:commands.Context, default):
    name = ctx.command.qualified_name.split(" ")[0]
    if ctx.guild is None:
        return default
    command_overrides = Configuration.getConfigVar(ctx.guild.id, "COMMAND_OVERRIDES")
    cog_overrides = Configuration.getConfigVar(ctx.guild.id, "COG_OVERRIDES")
    cog_name = type(ctx.cog).__name__

    if name in command_overrides:
        return check_perm_lvl(ctx, command_overrides[name])
    elif cog_name in cog_overrides:
        return check_perm_lvl(ctx, cog_overrides[cog_name])
    else:
        return default

def public(ctx):
    return True

def disabled(ctx):
    return False

perm_checks = [
    public,
    is_trusted,
    is_mod,
    is_admin,
    is_server_owner,
    disabled
]

def check_perm_lvl(ctx, lvl):
    return perm_checks[lvl](ctx)
