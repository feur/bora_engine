# api/resources.py

from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from api.models import Agent
from api.models import Event



    
"""
Agent model
PID : process id of agent in the host
Currency : currency that the agent is trading
Base : base currency that the agent is using
Exchange : exchnage that the agent is trading in
Weight : trading weight
Limit : limit
host : agent host IP
key : exchange key
api : exchange api
"""

class AgentResource(ModelResource):
    class Meta:
        queryset = Agent.objects.all()
        resource_name = 'agent'
        authorization = Authorization()
        filtering = {
            'pid': 'exact',
            'currency': 'iexact',
            'base': 'iexact',
            'email': 'iexact',
            'user_type': ALL,
            'user_status': ALL,
        }
        
       
"""
Event fields:
    event_id
    event_type
    user_id
    event_status
    event_occured_at
"""

      
class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        authorization = Authorization()
        filtering = {
            'event_id': 'exact',
            'event_type': 'iexact',
            'user_id': 'iexact',
            'email': 'iexact',
            'event_status': ALL,
        }
        
     
        
