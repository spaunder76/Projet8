from django import template

register = template.Library()

@register.filter
def is_following_user(user, other_user):
    return user.following.filter(pk=other_user.pk).exists()
