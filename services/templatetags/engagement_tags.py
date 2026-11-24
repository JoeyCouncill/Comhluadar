from django import template
from services.engagements import requests_for_participant, can_reopen_request


register = template.Library()

### Used to determine if a chat has a linked listing so it can show it ###
@register.simple_tag
def listing_request_for_chat(chat, user):
    return requests_for_participant(user).filter(chat=chat).first()


### Used to determine which user may reopen an engagement request ###
@register.simple_tag
def may_reopen_engagement_request(item, user):
    return can_reopen_request(item, user)