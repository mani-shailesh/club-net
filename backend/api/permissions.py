"""
This module declares the custom Permission classes.
"""

from rest_framework import permissions
from . import models


def is_secretary(user_obj):
    """A helper function to check if the `user_obj` is a secretary"""
    return user_obj.is_superuser


class IsRepOrReadOnlyPost(permissions.BasePermission):
    """
    Custom permission to allow everyone to read posts but only allow
    representative of a club to update or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the club representative.
        return models.ClubMembership.objects.filter(
            user__id=request.user.id,
            club_role__club=obj.channel.club,
            club_role__privilege='REP'
        ).exists()


class IsClubMemberReadOnlyConversation(permissions.BasePermission):
    """
    Custom permission to allow only club members to read conversations and do
    not allow anyone to write.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to only club members
        if request.method in permissions.SAFE_METHODS:
            return models.ClubMembership.objects.filter(
                user__id=request.user.id,
                club_role__club=obj.channel.club
            ).exists()

        # Write permissions are denied to everyone.
        return False


class IsSelfOrReadOnlyUser(permissions.BasePermission):
    """
    Custom permission to only allow a user to update his/her details but see
    details of everyone.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow a user to edit his/her details
        return obj == request.user


class IsSecyOrRepOrReadOnlyClub(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative to
    write but allow everyone to read the details of a club.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow a secretary to delete
        if request.method == 'DELETE':
            return is_secretary(request.user)
        # Only allow a secretary or club representative to update
        return is_secretary(request.user) or \
            models.ClubMembership.objects.filter(
                user__id=request.user.id,
                club_role__club=obj,
                club_role__privilege='REP').exists()


class IsRepClubRole(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to access a
    clubRole.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow the club representative
        return models.ClubMembership.objects.filter(
            user__id=request.user.id,
            club_role__club=obj.club,
            club_role__privilege='REP').exists()


class IsRepClubMembership(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to access a
    clubMembership.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow the club representative
        return models.ClubMembership.objects.filter(
            user__id=request.user.id,
            club_role__club=obj.club_role.club,
            club_role__privilege='REP').exists()


class IsSecyOrRepOrAuthorFeedback(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative or
    author to read the details of a feedback.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.author == request.user \
                    or is_secretary(request.user) \
                    or models.ClubMembership.objects.filter(
                        user__id=request.user.id,
                        club_role__club=obj.club,
                        club_role__privilege='REP').exists()
        # Do not allow write permissions to anyone
        return False


class IsSecyOrRepOrAuthorFeedbackReply(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative
    or author to read the details of a feedbackReply.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.parent.author == request.user \
                    or is_secretary(request.user) \
                    or models.ClubMembership.objects.filter(
                        user__id=request.user.id,
                        club_role__club=obj.parent.club,
                        club_role__privilege='REP').exists()
        # Do not allow write permissions to anyone
        return False


class IsRepOrSecyAndClubMemberReadOnlyProject(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club members to read
    the details of a project. Also, to allow a club representative to update
    the details of a project.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return is_secretary(request.user) \
                    or models.ClubMembership.objects.filter(
                        user__id=request.user.id,
                        club_role__club__in=obj.clubs.all()
                    ).exists()
        # Allow write permissions to only the club representative
        return models.ClubMembership.objects.filter(
            user__id=request.user.id,
            club_role__club__in=obj.clubs.all(),
            club_role__privilege='REP'
        ).exists()
