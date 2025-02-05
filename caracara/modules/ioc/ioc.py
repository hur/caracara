"""Falcon IOC API."""

from functools import partial
from typing import Dict, List, Union

import falconpy

from caracara.common.exceptions import MustProvideFilter, IocNotFound
from caracara.common.module import FalconApiModule, ModuleMapper
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string
from caracara.modules.ioc.indicator import IOC


# instrument falconpy to raise exceptions and log warnings
def instr(func, logger) -> dict:
    """Instrument FalconPy functions with basic error handling warning logging.

    This is an internal function, and therefore developers should not expect this function to
    remain consistent.
    """

    def handle_errors(*args, **kwargs):
        response = func(*args, **kwargs)
        errors = response["body"].get("errors", []) or []

        # Some IOC APIs provide additional error information in the returned resources. This is useful to expose
        # to the user as it provides detailed information about why a request failed.
        if response["body"]["resources"]:
            for resource in response["body"]["resources"]:
                if isinstance(resource, dict) and resource.get("message_type") == "error":
                    errors.append(f"field_name: {resource.get('field_name')}, error: {resource.get('message')}")
            
                if isinstance(resource, dict) and resource.get("message_type") == "warning":
                    logger.warning(resource.get("message"))
        if len(errors) == 0:
            return response
        raise ValueError(errors)

    return handle_errors


class IocApiModule(FalconApiModule):
    """
    This module provides the logic to interact with the Falcon IOC API.
    """

    name = "CrowdStrike IOC API Module"
    help = "Interact with Falcon IOCs within your tenant."

    def __init__(self, api_authentication: falconpy.OAuth2, mapper: ModuleMapper):
        """Construct an instance of the IocApiModule class."""
        super().__init__(api_authentication, mapper)
        self.logger.debug("Configuring the FalconPy IOC API")
        self.ioc_api = falconpy.IOC(auth_object=self.api_authentication)
        self.actions_cache = {}

    
    def _search_iocs(
        self, filters: Union[FalconFilter, str] = None
    ) -> List[Dict]:
        """Return a list of dictionaries containing all IOCs."""
        
        self.logger.info("Describing all Falcon IOCs")
        partial_func = partial(
            instr(self.ioc_api.indicator_search, self.logger),
            filter=filters,
        )

        resources = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        #self.logger.debug(resources)
        return resources
    
    @filter_string
    def describe_iocs(
        self, filters: Union[FalconFilter, str] = None
    ) -> List[IOC]:
        """Return a list of IOCs matching the specified filter
        
        Arguments
        ---------
        filters: Union[FalconFilter, str], optional
            Filters to apply to the IOC search.

        Returns
        -------
        List[IOC]: The IOCs matching the specified filter.
        """
        raw_iocs_list = self._search_iocs(filters=filters)
        
        if not raw_iocs_list:
            raise IocNotFound

        iocs = self._get_iocs(raw_iocs_list)
        
        return iocs
    
    def _get_iocs(self, ids: List[str]) -> List[IOC]:
        """Get IOCs by their id."""
        partial_func = partial(
            instr(self.ioc_api.indicator_get, self.logger),
            ids=ids,
        )
        response = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        iocs = []
        for ioc_dict in response:
            self.logger.info(ioc_dict)
            ioc = IOC.from_data_dict(data_dict=ioc_dict)
            iocs.append(ioc)
            
        return iocs
    
    def create(
        self, 
        ioc: IOC, 
        comment: str = "",
        retrodetects: bool = False,
        ignore_warnings: bool = False,
    ) -> IOC:
        """Create an IOC
        
        Arguments
        ---------
        ioc: IOC
            the IOC object that should be created in the cloud.
        comment: str
            Audit log comment. Defaults to empty.
        retrodetects: bool
            Whether to submit to retrodetects. Defaults to false.
        ignore_warnings: bool
            Set to true to ignore warnings and add all IOCs. Defaults to false.

        Returns
        -------
        IOC: The created IOC.
        """
        #if not self.actions_cache:
        #    self._populate_actions_cache()
        
        return self.create_batch([ioc], comment, retrodetects, ignore_warnings)[0]
    
    def create_batch(
        self, 
        iocs: List[IOC], 
        comment: str,
        retrodetects: bool,
        ignore_warnings: bool,
    ) -> List[IOC]:
        """Create a collection of IOCs.
        
        Arguments
        ---------
        ioc: List[IOC]
            A list containing the IOC objects that should be created in the cloud.
        comment: str
            Audit log comment. Defaults to empty.
        retrodetects: bool
            Whether to submit to retrodetects. Defaults to false.
        ignore_warnings: bool
            Set to true to ignore warnings and add all IOCs. Defaults to false.

        Returns
        -------
        List[IOC]: A list of the created IOCs.
        """
        #if not self.actions_cache:
        #    self._populate_actions_cache()
        
        #for ioc in iocs:
        #    ioc.validate(self.actions_cache)
        
        iocs_dump = [ioc.dump() for ioc in iocs]
        

        response = instr(self.ioc_api.indicator_create, self.logger)(indicators=iocs_dump, retrodetects=retrodetects, ignore_warnings=ignore_warnings, comment=comment)
        
        self.logger.info(response)
        clouded_iocs = [IOC.from_data_dict(ioc_raw) for ioc_raw in response["body"]["resources"]]
        return clouded_iocs
    
    def update(
        self,
        ioc: IOC,
        comment: str = None,
        retrodetects: bool = False,
        ignore_warnings: bool = False,
    ) -> IOC:
        """Update an IOC.
        
        Arguments
        ---------
        ioc: IOC
            the IOC object that should be updated in the cloud.
        comment: str
            Audit log comment. Defaults to empty.
        retrodetects: bool
            Whether to submit to retrodetects. Defaults to false.
        ignore_warnings: bool
            Set to true to ignore warnings and add all IOCs. Defaults to false.

        Returns
        -------
        IOC: The updated IOC.
        """
        return self.update_batch(self, [ioc], comment, retrodetects, ignore_warnings)[0]
    
    def update_batch(
        self, 
        iocs: List[IOC], 
        comment: str = None,
        retrodetects: bool = False, 
        ignore_warnings: bool = False,
    ) -> List[IOC]:
        """Update a collection of IOCs.
        
        Arguments
        ---------
        ioc: List[IOC]
            A list containing the IOC objects that should be updated in the cloud.
        comment: str
            Audit log comment. Defaults to empty.
        retrodetects: bool
            Whether to submit to retrodetects. Defaults to false.
        ignore_warnings: bool
            Set to true to ignore warnings and add all IOCs. Defaults to false.

        Returns
        -------
        List[IOC]: A list of the updated IOCs.
        """
        #if not self.actions_cache:
        #    self._populate_actions_cache()

        #for ioc in iocs:
        #    ioc.validate()

        iocs_dump = [ioc.dump() for ioc in iocs]

        response = instr(self.ioc_api.indicator_update, self.logger)(
            indicators=iocs_dump,
            retrodetects=retrodetects,
            ignore_warnings=ignore_warnings,
            comment=comment,
        )

        clouded_iocs = [IOC.from_data_dict(ioc_raw) for ioc_raw in response["body"]["resources"]]
        return clouded_iocs
    

    def delete(self, ioc: IOC, comment: str) -> str:
        """Delete an IOC.
        
        Arguments
        ---------
        ioc: IOC
            the IOC object that should be deleted in the cloud.
        comment: str
            Audit log comment. Defaults to empty.

        Returns
        -------
        IOC: The id of the deleted IOC.
        """
        return self.delete_batch(iocs=[ioc], comment=comment)[0]
    
    def delete_batch(self, iocs: List[IOC], comment: str) -> List[str]:
        """Delete a collection of IOCs.
        
        Arguments
        ---------
        ioc: List[IOC]
            A list containing the IOC objects that should be deleted in the cloud.
        comment: str
            Audit log comment. Defaults to empty.

        Returns
        -------
        List[str]: A list of ids of the deleted IOCs.
        """
        ioc_ids = [ioc.id for ioc in iocs]

        response = instr(self.ioc_api.indicator_delete, self.logger)(
            ids=ioc_ids,
            comment=comment,
            from_parent=False
        )

        deleted_ids = response["body"]["resources"]
        if deleted_ids is None:
            raise IocNotFound
        
        return deleted_ids


    @filter_string
    def delete_by_filter(self, filters: Union[FalconFilter, str], comment: str = "") -> List[str]:
        """Delete a collection of IOCs matching a filter.
        
        Arguments
        ---------
        ioc: List[IOC]
            A list containing the IOC objects that should be deleted in the cloud.
        filters: Union[FalconFilter, str]
            Filters to apply to the IOC search.
        comment: str, optional
            Audit log comment. Defaults to empty.

        Returns
        -------
        List[str]: A list of ids of the deleted IOCs.
        """
        # Prevent accidental delete all operations
        if not filters:
            raise MustProvideFilter
        
        # Obtain IDs of IOCs matching the filter
        iocs = self.describe_iocs(filters)
        
        # Delete the IOCs
        response = instr(self.ioc_api.indicator_delete, self.logger)(
            ids=[ioc.id for ioc in iocs],
            comment=comment,
            from_parent=False
        )
        
        deleted_ids = response["body"]["resources"]
        if deleted_ids is None:
            raise IocNotFound
        
        # Return a list of IOC IDs that were deleted
        return deleted_ids

    def _populate_actions_cache(self):
        """Retrieve and cache valid actions types and related data from the Falcon cloud."""
        response = instr(self.ioc_api.action_get, self.logger)()

        for action in response["body"]["resources"]:
            # /iocs/entities/actions/v1 returns an action called "none" instead of "no_action"
            # We need to map "none" to "no_action" since the other API endpoints expect "no_action" 
            # and do not accept "none"
            if action["id"] == "none":
                action["id"] = "no_action"
            self.actions_cache[action["id"]] = action

