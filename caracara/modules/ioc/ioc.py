"""Falcon IOC API."""

from functools import partial
from typing import Dict, List, Union

import falconpy

from caracara.common.exceptions import MustProvideFilter, IocNotFound
from caracara.common.module import FalconApiModule, ModuleMapper
from caracara.common.pagination import all_pages_numbered_offset_parallel, all_pages_token_offset
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string
from caracara.modules.ioc.indicator import IOC


# instrument falconpy to raise exceptions and log warnings
def instr(func, logger, ignore_warnings: bool = False) -> dict:
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
                    if not ignore_warnings:
                        errors.append(resource.get("message"))
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
        """Return a list of dictionaries containing all IOCs matching the specified filter.
        
        Arguments
        ---------
        filters: Union[FalconFilter, str], optional
            Filters to apply to the IOC search. If not specified, return all IOCs.
        
        Returns
        -------
        List[Dict]: The raw IOCs matching the specified filter, as returned by the API.

        """
        
        self.logger.info(f"Describing Falcon IOCs matching filter `{filters}`")
        partial_func = partial(
            instr(self.ioc_api.indicator_search, self.logger),
            filter=filters,
        )

        resources = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        return resources
    

    @filter_string
    def describe_iocs_raw(
        self, filters: Union[FalconFilter, str] = None
    ) -> List[Dict]:
        """Return a list of IOCs matching the specified filter
        
        Arguments
        ---------
        filters: Union[FalconFilter, str], optional
            Filters to apply to the IOC search.

        Returns
        -------
        List[Dict]: The raw IOCs matching the specified filter, as returned by the API.
        """
        ioc_ids = self._search_iocs(filters=filters)
        
        if not ioc_ids:
            raise IocNotFound

        raw_iocs = self._get_iocs_raw(ioc_ids)
    
        return raw_iocs
    

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
        ioc_ids = self._search_iocs(filters=filters)
        
        if not ioc_ids:
            raise IocNotFound

        raw_iocs = self._get_iocs_raw(ioc_ids)
        
        iocs = []
        for ioc_dict in raw_iocs:
            ioc = IOC._from_api_response(ioc_dict)
            iocs.append(ioc)

        return iocs
    
    def _get_iocs_raw(self, ids: List[str]) -> List[IOC]:
        """Get IOCs by their id."""
        partial_func = partial(
            instr(self.ioc_api.indicator_get, self.logger),
            ids=ids,
        )
        raw_iocs = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
            
        return raw_iocs
    

    def create(
        self,
        **kwargs,
    ) -> List[IOC]:
        """Create IOCs. This is a thin paginated wrapper around FalconPy's indicator_create.
        
        Arguments
        ---------
        **kwargs
            Keyword arguments passed to FalconPy.
            For detailed information, see 
            https://www.falconpy.io/Service-Collections/IOC.html#indicator_create_v1
            
            An example use of this method can be found in examples/ioc/create_ioc.py
        
        Returns
        -------
        List[IOC]
            A list of the created IOC objects.
        """

        response = instr(
            self.ioc_api.indicator_create, 
            self.logger, 
            kwargs.get("ignore_warnings", False)
        )(**kwargs)

        iocs = [IOC._from_api_response(ioc_raw) for ioc_raw in response["body"]["resources"]]
        return iocs
    
    
    def update(
        self, 
        iocs: Union[List[IOC], IOC], 
        comment: str,
        retrodetects: bool = False, 
        ignore_warnings: bool = False,
    ) -> List[IOC]:
        """Update a collection of IOCs.
        
        Arguments
        ---------
        ioc: Union[List[IOC], IOC]
            An IOC object, or a list of IOC objects, that should be updated in the cloud.
        comment: str
            Audit log comment.
        retrodetects: bool
            Whether to submit to retrodetects. Defaults to false.
        ignore_warnings: bool
            Set to true to ignore warnings and add all IOCs. Defaults to false.

        Returns
        -------
        List[IOC]: A list of the updated IOCs.
        """
        if isinstance(iocs, IOC):
            iocs = [iocs]
        
        iocs_dump = [ioc._to_api_request() for ioc in iocs]

        response = instr(self.ioc_api.indicator_update, self.logger, ignore_warnings=ignore_warnings)(
            indicators=iocs_dump,
            retrodetects=retrodetects,
            ignore_warnings=ignore_warnings,
            comment=comment)
        
        clouded_iocs = [IOC._from_api_response(ioc_raw) for ioc_raw in response["body"]["resources"]]

        if not clouded_iocs:
            raise IocNotFound
        
        return clouded_iocs
    

    def delete(self, iocs: Union[List[IOC], IOC], comment: str) -> List[str]:
        """Delete a collection of IOCs.
        
        Arguments
        ---------
        ioc: Union[List[IOC], IOC]
            An IOC object, or a list of IOC objects, that should be deleted in the cloud.
        comment: str
            Audit log comment.

        Returns
        -------
        List[str]: A list of ids of the deleted IOCs.
        """
        if isinstance(iocs, IOC):
            iocs = [iocs]
        
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