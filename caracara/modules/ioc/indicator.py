
from datetime import datetime

from typing import Dict, List, Union

class IOC:
    """A clas representing an IOC."""

    id: str
    type: str
    value: str
    action: str
    mobile_action: str
    severity: str
    host_groups: List[str]
    metadata: Dict
    platforms: List[str]
    tags: List[str]
    expiration: str
    expired: bool
    deleted: bool
    description: str
    applied_globally: bool
    from_parent: bool
    parent_cid_name: str
    created_on: str
    created_by: str
    modified_on: str
    modified_by: str
    source: str

    def __init__(self, **kwargs):
        """Create a new IOC object."""
        self.type = kwargs["type"]
        self.description = kwargs.get("description", None)
        self.value = kwargs["value"]
        self.action = kwargs["action"]
        self.applied_globally = kwargs["applied_globally"]
        self.source = kwargs.get("source", None)
        self.severity = kwargs.get("severity", None)
        self.platforms = kwargs.get("platforms", [])
        self.tags = kwargs.get("tags", [])
        self.mobile_action = kwargs.get("mobile_action", None)
        self.host_groups = kwargs.get("host_groups", None)

        self.metadata =  {"filename": kwargs["filename"]} if "filename" in kwargs else {}

        expiration = kwargs.get("expiration", None)
        if expiration is None:
            pass
        elif isinstance(expiration, datetime):
            self.expiration = expiration.isoformat()
        elif isinstance(expiration, str):
            self.expiration = expiration
        else:
            raise ValueError("expiration must be datetime or str")
        
        self.expired = None
        self.deleted = None
        self.id = None
        self.from_parent = None
        self.parent_cid_name = None
        self.created_on = None
        self.created_by = None
        self.modified_on = None
        self.modified_by = None

        

    @staticmethod
    def from_data_dict(data_dict: dict):
        """Construct a IOC object from an instance of the `api.IndicatorV1` API model.
        """
        ioc = IOC(
            type=data_dict.get("type", None), 
            value=data_dict.get("value", None), 
            action=data_dict.get("action", None),
            applied_globally=data_dict.get("applied_globally", None),
        )

        ioc.id = data_dict.get("id", None)
        ioc.mobile_action = data_dict.get("mobile_action", None)
        ioc.description = data_dict.get("description", None)
        ioc.host_groups = data_dict.get("host_groups", [])
        ioc.severity = data_dict.get("severity", None)
        ioc.metadata = data_dict.get("metadata", {})
        ioc.platforms = data_dict.get("platforms", [])
        ioc.tags = data_dict.get("tags", [])
        # Expiration is not always populated.
        ioc.expiration = data_dict.get("expiration", None)
        ioc.expired = data_dict.get("expired", None)
        ioc.deleted = data_dict.get("deleted", None)
        ioc.from_parent = data_dict.get("from_parent", None)
        ioc.parent_cid_name = data_dict.get("parent_cid_name", None)
        ioc.created_on = data_dict.get("created_on", None)
        ioc.created_by = data_dict.get("created_by", None)
        ioc.modified_on = data_dict.get("modified_on", None)
        ioc.modified_by = data_dict.get("modified_by", None)
        ioc.source = data_dict.get("source", None)
        
        return ioc
    
    def dump(self) -> dict:
        if self.exists_in_cloud():
            return {
                "id": self.id,
                "type": self.type,
                "value": self.value,
                "action": self.action,
                "mobile_action": self.mobile_action,
                "severity": self.severity,
                "host_groups": self.host_groups,
                "metadata": self.metadata,
                "platforms": self.platforms,
                "tags": self.tags,
                "expiration": self.expiration,
                "expired": self.expired,
                "deleted": self.deleted,
                "description": self.description,
                "applied_globally": self.applied_globally,
                "from_parent": self.from_parent,
                "parent_cid_name": self.parent_cid_name,
                "created_on": self.created_on,
                "created_by": self.created_by,
                "modified_on": self.modified_on,
                "modified_by": self.modified_by,
                "source": self.source,
            }
        else:
            res = {}
            for key in [
                "type", "description", "value", "action", "applied_globally", "source", "severity",
                "platforms", "tags", "mobile_action", "host_groups"
                ]:
                val = getattr(self, key)
                #if val not in (None, []):
                #    res[key] = val
            return res
    
    
    def exists_in_cloud(self) -> bool:
        return self.id is not None
    
    def validate(self, actions_cache):
        valid_action = self.action in actions_cache
        if not valid_action:
            raise ValueError(f"Invalid action '{self.action}', valid options: {actions_cache.keys()}")
        
        if len(actions_cache[self.action]) > 0:
            valid_severity = self.severity in actions_cache[self.action]
        else:
            valid_severity = self.severity == None
        if not valid_severity:
            if len(actions_cache[self.action] > 0):
                raise ValueError(f"Invalid severity '{self.severity}', valid options: {actions_cache[self.action]}")
            else:
                raise ValueError(f"Severity not supported by this action - set severity to None")

        valid_type = self.type in actions_cache[self.action]["platforms_by_type"]
        if not valid_type:
            raise ValueError(f"Invalid type {self.type}, valid options: {actions_cache[self.action]['platforms_by_type'].keys()}")
        
        valid_platform = all(
            platform in actions_cache[self.action]["platforms_by_type"][self.type] 
            for platform in self.platforms
        )
        if not valid_platform:
            raise ValueError(f"Invalid platform(s) {self.platforms}, valid options: {actions_cache[self.action]['platforms_by_type'][self.type]}")
