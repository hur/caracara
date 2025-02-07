
from attrs import define, field
from attrs.setters import frozen
#from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List

from caracara.modules.ioc._dataclass_utils import Frozen


@define
class IOC:
    """A class representing an IOC returned by the Falcon API."""
    type: str
    value: str
    action: str
    mobile_action: str
    description: str
    severity: str
    applied_globally: bool
    host_groups: List[str]
    metadata: Dict
    platforms: List[str]
    tags: List[str]
    expiration: str
    source: str

    # Returned by the API, not intended to be modifiable by the client.
    id: str = field(on_setattr=frozen)
    expired: bool = field(on_setattr=frozen)
    deleted: bool = field(on_setattr=frozen)
    from_parent: bool = field(on_setattr=frozen)
    parent_cid_name: str = field(on_setattr=frozen)
    created_on: str = field(on_setattr=frozen)
    created_by: str = field(on_setattr=frozen)
    modified_on: str = field(on_setattr=frozen)
    modified_by: str = field(on_setattr=frozen)
    

    @classmethod
    def _from_api_response(cls, data):
        """Construct an IOC object from a Falcon API response's data."""
        return cls(
            id = data["id"],
            type = data["type"],
            value = data["value"],
            action = data["action"],
            mobile_action = data.get("mobile_action"),
            severity = data["severity"],
            platforms = data["platforms"],
            description = data.get("description"),
            expiration = data.get("expiration"),
            host_groups = data.get("host_groups"),
            metadata = data.get("metadata"),
            tags = data.get("tags"),
            applied_globally = data.get("applied_globally"),
            source = data.get("source"),
            created_on = data["created_on"],
            created_by = data["created_by"],
            modified_on = data["modified_on"],
            modified_by = data["modified_by"],
            from_parent = data["from_parent"],
            deleted = data["deleted"],
            expired = data["expired"],
            # Returned if from_parent = True
            parent_cid_name = data.get("parent_cid_name"),
        )
    
    def _to_api_request(self) -> Dict:
        """Return a Dict in the format expected by the create/update API endpoints.
        
        Returns
        ------
        Dict
            a Dict containing fields that can be modified by the client.
        """
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value,
            "action": self.action,
            "mobile_action": self.mobile_action,
            "severity": self.severity,
            "platforms": self.platforms,
            "description": self.description,
            "expiration": self.expiration,
            "metadata": self.metadata,
            "tags": self.tags,
            "applied_globally": self.applied_globally,
            "host_groups": self.host_groups,
            "source": self.source,
        }