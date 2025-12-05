#!/usr/bin/env python3
"""Analyze GoodData users, groups, and permissions."""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from gooddata_sdk import GoodDataSdk

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

host = os.getenv("GOODDATA_HOST")
token = os.getenv("GOODDATA_TOKEN")

if not host or not token:
    print("ERROR: GOODDATA_HOST and GOODDATA_TOKEN must be set in .env")
    sys.exit(1)

sdk = GoodDataSdk.create(host, token)

# Data structures to hold everything
data = {
    "users": [],
    "groups": [],
    "workspaces": [],
    "user_to_groups": defaultdict(list),
    "group_to_users": defaultdict(list),
    "group_hierarchy": defaultdict(list),  # parent -> children
    "workspace_permissions": defaultdict(list),
    "user_permissions": {},
    "group_permissions": {},
}

print("=" * 70)
print("GOODDATA USERS, GROUPS & PERMISSIONS ANALYSIS")
print("=" * 70)

# ============================================================================
# 1. FETCH ALL USERS
# ============================================================================
print("\n[1/7] Fetching users...")
try:
    users = sdk.catalog_user.list_users()
    for u in users:
        user_data = {
            "id": u.id,
            "name": getattr(u, "name", None),
            "email": getattr(u, "email", None),
            "auth_id": getattr(u, "auth_id", None),
        }
        data["users"].append(user_data)
    print(f"      Found {len(data['users'])} users")
except Exception as e:
    print(f"      Error: {e}")

# ============================================================================
# 2. FETCH ALL USER GROUPS
# ============================================================================
print("\n[2/7] Fetching user groups...")
try:
    groups = sdk.catalog_user.list_user_groups()
    for g in groups:
        group_data = {
            "id": g.id,
            "name": getattr(g, "name", None),
        }
        data["groups"].append(group_data)
    print(f"      Found {len(data['groups'])} groups")
except Exception as e:
    print(f"      Error: {e}")

# ============================================================================
# 3. FETCH USER-GROUP MEMBERSHIPS
# ============================================================================
print("\n[3/7] Fetching user-group memberships...")
try:
    decl_users = sdk.catalog_user.get_declarative_users()
    for u in decl_users.users:
        if u.user_groups:
            for ug in u.user_groups:
                data["user_to_groups"][u.id].append(ug.id)
                data["group_to_users"][ug.id].append(u.id)

    total_memberships = sum(len(g) for g in data["user_to_groups"].values())
    print(f"      Found {total_memberships} user-group memberships")
except Exception as e:
    print(f"      Error: {e}")

# ============================================================================
# 4. FETCH GROUP HIERARCHY (parent-child relationships)
# ============================================================================
print("\n[4/7] Fetching group hierarchy...")
try:
    decl_groups = sdk.catalog_user.get_declarative_user_groups()
    for g in decl_groups.user_groups:
        if g.parents:
            for parent in g.parents:
                data["group_hierarchy"][parent.id].append(g.id)

    hierarchies = sum(len(c) for c in data["group_hierarchy"].values())
    print(f"      Found {hierarchies} parent-child group relationships")
except Exception as e:
    print(f"      Error: {e}")

# ============================================================================
# 5. FETCH WORKSPACES
# ============================================================================
print("\n[5/7] Fetching workspaces...")
try:
    workspaces = sdk.catalog_workspace.list_workspaces()
    for ws in workspaces:
        ws_data = {
            "id": ws.id,
            "name": ws.name,
            "parent_id": getattr(ws, "parent_id", None),
        }
        data["workspaces"].append(ws_data)
    print(f"      Found {len(data['workspaces'])} workspaces")
except Exception as e:
    print(f"      Error: {e}")

# ============================================================================
# 6. FETCH WORKSPACE PERMISSIONS
# ============================================================================
print("\n[6/7] Fetching workspace permissions...")
try:
    for ws in data["workspaces"]:
        ws_id = ws["id"]
        try:
            perms = sdk.catalog_permission.get_declarative_permissions(ws_id)
            if perms.permissions:
                for p in perms.permissions:
                    perm_entry = {
                        "workspace_id": ws_id,
                        "assignee_id": p.assignee.id if p.assignee else None,
                        "assignee_type": p.assignee.type if p.assignee else None,
                        "name": p.name,
                    }
                    data["workspace_permissions"][ws_id].append(perm_entry)
        except Exception as e:
            # May not have permission to view this workspace's permissions
            pass

    total_perms = sum(len(p) for p in data["workspace_permissions"].values())
    print(f"      Found {total_perms} workspace permission assignments")
except Exception as e:
    print(f"      Error: {e}")

# ============================================================================
# 7. FETCH INDIVIDUAL USER/GROUP PERMISSIONS
# ============================================================================
print("\n[7/7] Fetching individual user and group permissions...")
try:
    for user in data["users"]:
        try:
            perms = sdk.catalog_user.get_user_permissions(user["id"])
            data["user_permissions"][user["id"]] = [
                {"workspace_id": p.workspace_id, "permission": p.name}
                for p in perms
            ] if perms else []
        except:
            pass

    for group in data["groups"]:
        try:
            perms = sdk.catalog_user.get_user_group_permissions(group["id"])
            data["group_permissions"][group["id"]] = [
                {"workspace_id": p.workspace_id, "permission": p.name}
                for p in perms
            ] if perms else []
        except:
            pass

    user_perms_count = sum(len(p) for p in data["user_permissions"].values())
    group_perms_count = sum(len(p) for p in data["group_permissions"].values())
    print(f"      Found {user_perms_count} user permissions, {group_perms_count} group permissions")
except Exception as e:
    print(f"      Error: {e}")

# ============================================================================
# OUTPUT RAW DATA
# ============================================================================
print("\n" + "=" * 70)
print("RAW DATA SUMMARY")
print("=" * 70)

print("\n### USERS ###")
for u in data["users"]:
    groups = data["user_to_groups"].get(u["id"], [])
    name = u.get('name') or 'N/A'
    print(f"  {u['id']:<30} | {name:<25} | Groups: {groups}")

print("\n### GROUPS ###")
for g in data["groups"]:
    members = data["group_to_users"].get(g["id"], [])
    children = data["group_hierarchy"].get(g["id"], [])
    name = g.get('name') or 'N/A'
    print(f"  {g['id']:<30} | {name:<25} | Members: {len(members)}, Children: {children}")

print("\n### WORKSPACES ###")
for ws in data["workspaces"]:
    perms = data["workspace_permissions"].get(ws["id"], [])
    name = ws.get('name') or 'N/A'
    print(f"  {ws['id']:<30} | {name:<30} | Permissions: {len(perms)}")

# ============================================================================
# PATTERN ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("PATTERN ANALYSIS")
print("=" * 70)

# Pattern 1: Users with no group memberships
users_no_groups = [u["id"] for u in data["users"] if not data["user_to_groups"].get(u["id"])]
print(f"\n[Pattern 1] Users with NO group memberships: {len(users_no_groups)}")
for uid in users_no_groups:
    print(f"  - {uid}")

# Pattern 2: Empty groups (no members)
empty_groups = [g["id"] for g in data["groups"] if not data["group_to_users"].get(g["id"])]
print(f"\n[Pattern 2] Empty groups (no members): {len(empty_groups)}")
for gid in empty_groups:
    print(f"  - {gid}")

# Pattern 3: Users with most group memberships
print(f"\n[Pattern 3] Users with most group memberships:")
sorted_users = sorted(data["user_to_groups"].items(), key=lambda x: len(x[1]), reverse=True)
for uid, groups in sorted_users[:5]:
    print(f"  - {uid}: {len(groups)} groups -> {groups}")

# Pattern 4: Groups with most members
print(f"\n[Pattern 4] Groups with most members:")
sorted_groups = sorted(data["group_to_users"].items(), key=lambda x: len(x[1]), reverse=True)
for gid, members in sorted_groups[:5]:
    print(f"  - {gid}: {len(members)} members")

# Pattern 5: Group hierarchy depth
print(f"\n[Pattern 5] Group hierarchy:")
if data["group_hierarchy"]:
    for parent, children in data["group_hierarchy"].items():
        print(f"  - {parent} -> {children}")
else:
    print("  No group hierarchies found (flat structure)")

# Pattern 6: Permission distribution by workspace
print(f"\n[Pattern 6] Permissions per workspace:")
for ws_id, perms in sorted(data["workspace_permissions"].items(), key=lambda x: len(x[1]), reverse=True):
    if perms:
        by_type = defaultdict(list)
        for p in perms:
            by_type[p["name"]].append(p["assignee_id"])
        print(f"  - {ws_id}:")
        for perm_name, assignees in by_type.items():
            print(f"      {perm_name}: {len(assignees)} assignees")

# ============================================================================
# ANOMALY DETECTION
# ============================================================================
print("\n" + "=" * 70)
print("ANOMALY DETECTION")
print("=" * 70)

anomalies = []

# Anomaly 1: Users with direct permissions (bypassing groups)
print("\n[Anomaly Check 1] Users with direct workspace permissions (not via groups):")
for ws_id, perms in data["workspace_permissions"].items():
    for p in perms:
        if p["assignee_type"] == "user":
            anomalies.append(f"Direct user permission: {p['assignee_id']} has '{p['name']}' on {ws_id}")
            print(f"  ! {p['assignee_id']} has direct '{p['name']}' on workspace '{ws_id}'")

# Anomaly 2: Users in many groups (over-privileged?)
print("\n[Anomaly Check 2] Users in excessive groups (>3):")
for uid, groups in data["user_to_groups"].items():
    if len(groups) > 3:
        anomalies.append(f"User {uid} is in {len(groups)} groups")
        print(f"  ! {uid} is in {len(groups)} groups: {groups}")

# Anomaly 3: Workspaces with no permissions assigned
print("\n[Anomaly Check 3] Workspaces with no explicit permissions:")
for ws in data["workspaces"]:
    if ws["id"] not in data["workspace_permissions"] or not data["workspace_permissions"][ws["id"]]:
        anomalies.append(f"Workspace {ws['id']} has no explicit permissions")
        print(f"  ! {ws['id']} ({ws.get('name', 'N/A')}) has no explicit permissions")

# Anomaly 4: Orphaned groups (no parent, no members, not used in permissions)
print("\n[Anomaly Check 4] Potentially orphaned groups:")
used_groups = set()
for perms in data["workspace_permissions"].values():
    for p in perms:
        if p["assignee_type"] == "userGroup":
            used_groups.add(p["assignee_id"])

for g in data["groups"]:
    gid = g["id"]
    has_members = bool(data["group_to_users"].get(gid))
    is_parent = gid in data["group_hierarchy"]
    is_used = gid in used_groups

    if not has_members and not is_parent and not is_used:
        anomalies.append(f"Orphaned group: {gid}")
        print(f"  ! {gid} has no members, no children, and no workspace permissions")

# Anomaly 5: Duplicate permission patterns
print("\n[Anomaly Check 5] Users with identical group memberships:")
membership_patterns = defaultdict(list)
for uid, groups in data["user_to_groups"].items():
    pattern = tuple(sorted(groups))
    if pattern:  # Only non-empty patterns
        membership_patterns[pattern].append(uid)

for pattern, users in membership_patterns.items():
    if len(users) > 1:
        print(f"  Users with same groups {list(pattern)}:")
        for u in users:
            print(f"    - {u}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total Users:      {len(data['users'])}")
print(f"Total Groups:     {len(data['groups'])}")
print(f"Total Workspaces: {len(data['workspaces'])}")
print(f"Total Anomalies:  {len(anomalies)}")

# Save raw data to JSON for further analysis
output_file = Path(__file__).parent / "permissions_data.json"
with open(output_file, "w") as f:
    # Convert defaultdicts to regular dicts for JSON serialization
    output_data = {
        "users": data["users"],
        "groups": data["groups"],
        "workspaces": data["workspaces"],
        "user_to_groups": dict(data["user_to_groups"]),
        "group_to_users": dict(data["group_to_users"]),
        "group_hierarchy": dict(data["group_hierarchy"]),
        "workspace_permissions": dict(data["workspace_permissions"]),
        "user_permissions": data["user_permissions"],
        "group_permissions": data["group_permissions"],
        "anomalies": anomalies,
    }
    json.dump(output_data, f, indent=2)
print(f"\nRaw data saved to: {output_file}")
