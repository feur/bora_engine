from django.db import models
# Create your models here.


"""
Agent model
PID : process id of agent in the host
Currency : currency that the agent is trading
Base : base currency that the agent is using
Exchange : exchange that the agent is trading in
Weight : trading weight
Limit : limit
host : agent host IP
key : exchange key
api : exchange api
action: status of the agent

"""
class Agent(models.Model):
    pid = models.CharField(max_length=256, blank=True)
    currency = models.CharField(max_length=256, blank=True)
    exchange = models.CharField(max_length=256, blank=True)
    base = models.CharField(max_length=256, blank=True)
    weight = models.CharField(max_length=256, blank=True)
    limit = models.CharField(max_length=256, blank=True)
    host = models.CharField(max_length=256, blank=True)
    key = models.CharField(max_length=256, blank=True)
    secret = models.CharField(max_length=256, blank=True)
    action =  models.CharField(max_length=256, blank=True) ##"run" "stop" "pause" "purge"
    
    def __str__(self):
        return '%s %s %s %s %s %s %s' % (self.pid, self.currency, self.base, self.weight, self.limit, self.host) 



"""
Event Model, model used for recording Events
"""

class Event(models.Model):
    
    EVENT_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('HANDLED', 'HANDLED'),
        ('IGNORED', 'IGNORED'),
    )
    
    event_status  = models.CharField(max_length=512,choices=EVENT_STATUS_CHOICES,default='NEW')
    
    event_id = models.CharField(max_length=128)
    event_type = models.CharField(max_length=64)
    user_id  = models.CharField(max_length=512)
    event_occured_at  = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s %s %s %s %s %s %s' % (self.event_id, self.event_type, self.user_id, self.event_status, self.event_occured_at)
    
    
    
    
