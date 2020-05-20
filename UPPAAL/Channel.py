class Channel:
    ''' UPPAAL channel
    
    :param name: channel name
    :param type: channel type: broadcast ("b") or handshake ("h")
    :param urg: urgent or not'''
    def __init__(self, name, type, urg):
        self.name = name
        # "b" or "h"
        self.type = type
        # True of False
        self.urg = urg
        
    def isUrgent(self):
        ''' :returns: self.urg '''
        return self.urg
    
    def isBroadcast(self):
        ''' :returns: self.type '''
        return self.type == "b"
    
    def __str__(self):
        s = ""
        if self.isUrgent():
            s += "urgent "
        if self.isBroadcast():
            s += "broadcast "
        s += "chan " + self.name + ";"
        return s
    