import logging
from typing import Any, List, Union, Dict, Mapping

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor


class BaseDatabase:
    def __init__(self, database_name: str) -> None:
        self._client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
        self._database = self._client["synth"]
        self.collection = self._database[database_name]
        self.collection_cache: Dict[Any, Any] = {}
        self.name = database_name

    def _add_to_cache(self, param_filter: Dict[str, Any]) -> Any:
        """
        :param param_filter: dictionary to add
        :return: added item
        """
        if _id := param_filter.get("id", None):
            param_filter.pop("id")
        elif _id := param_filter.get("guild_id", None):
            param_filter.pop("guild_id")
        elif _id := param_filter.get("_id", None):
            param_filter.pop("_id")

        self.collection_cache[_id] = param_filter
        return param_filter

    def _update_cache(
        self, _id: Union[Dict[str, Any], int], new_value: Dict[str, Any]
    ) -> None:
        """
        Update an item in the cache based on the old and new values.

        :param _id: _Id of the item to update
        :param new_value: New values to update the item in the cache.
        """

        global id_to_update

        id_to_update = (
            _id.get("guild_id", None)
            or _id.get("id", None)
            or _id.get("_id", None)
            or _id
        )

        # self.collection_cache.setdefault(id_to_update, {}).update(new_value)
        if self.collection_cache.get(id_to_update, None):
            self.collection_cache[id_to_update] = _id
        else:
            self.collection_cache.get(id_to_update).update(new_value)

        return

    def _remove_from_cache(self, _id: Union[Dict[str, Any], int]) -> Any:
        """
        Remove an item from the cache based on the provided filter.

        :param param_filter: Filter criteria for finding the item to remove from the cache.
        :return: The removed item, or None if not found.
        """

        id_to_delete = (
            _id.get("id", None)
            or _id.get("guild_id", None)
            or _id.get("_id", None)
            or _id
        )

        del self.collection_cache[id_to_delete]
        return

    async def get_items_in_db(
        self,
        find_dict: Dict[str, Any],
        to_list: bool = True,
        count: Union[int, None] = None,
    ) -> Union[List[Mapping[str, Any]], AsyncIOMotorCursor]:
        result = self.collection.find(filter=find_dict)
        if to_list:
            return await result.to_list(length=count)

        return result

    def get_items_in_cache(
        self, query: Dict[Any, Any], to_return: str = None
    ) -> Union[List[Dict[Union[int, str], Dict[str, Any]]], Dict[str, Any]]:
        """
        Get items from cache by search query

        Args:
            query (Dict[int, Any]): Query to search

        Returns:
            List[Dict[int, Dict[str, Any]]]: List of items in query
        """
        if _id := query.get("id", None):
            query.pop("id")
        elif _id := query.get("guild_id", None):
            query.pop("guild_id")
        elif _id := query.get("_id", None):
            query.pop("_id")

        if result := self.collection_cache.get(_id, {}):
            if to_return:
                return result.get(to_return, None)
            return result

        # for key, value in self.collection_cache.items():
        #     if isinstance(query, (str, int)):
        #         if query in value.values() or query in value.keys():
        #             result.append({key: value})
        #         else:
        #             if isinstance(query, dict):
        #                 for sub_key, sub_value in value.items():
        #                     if query in sub_value.values() or query in sub_value.keys():
        #                         result.append({key: value})
        #                         break
        #             else:
        #                 for sub_value in value:
        #                     print(sub_value)
        #                     print(query)
        #                     if isinstance(query, dict):
        #                         print(sub_value.keys(), sub_value)
        #                         if query in sub_value.values() or query in sub_value.keys():
        #                             result.append({key: value})
        #                             break
        #                     elif isinstance(query, (str, int, bool)):
        #                         if query == sub_value:
        #                             result.append({key: value})
        #                             break
        #                     elif isinstance(query, list):
        #                         for sub_sub_value in sub_value:
        #                             if query == sub_sub_value:
        #                                 result.append({key: value})
        #                                 break
        # if query in sub_value

        # for key, value in self.collection_cache.items():
        #     if isinstance(query, (str, int)):
        #         if query in value.values() or query in value.keys():
        #             result.append({key: value})
        #     else:
        #         for inner_query in query.values():
        #             if isinstance(inner_query, dict) and all(
        #                 k in value and value[k] == v for k, v in inner_query.items()
        #             ):
        #                 result.append({key: value})
        #                 break
        #             elif inner_query in value.values() or inner_query in value.keys():
        #                 result.append({key: value})
        #                 break

    async def find_one_from_cache(self, value: Dict[str, Any]) -> Any:
        results = self.get_items_in_cache(value)
        return results[0] if results else None

    async def find_one_from_db(
        self, param_filter: Dict[str, Any]
    ) -> Mapping[str, Any] | None:
        results = await self.get_items_in_db(find_dict=param_filter, to_list=True)
        return results[0] if len(results) >= 1 else None

    async def find_one(
        self, value: Union[Dict[str, Any], Any], return_first_result: bool = False
    ) -> Any:
        # try to search in cache
        results = self.get_items_in_cache(value)
        if results:
            if len(results[0].get(1, [])) >= 1:
                return results[0].get(1, []) if return_first_result else results

        # if not found in cache, search in database
        results = await self.get_items_in_db(value, to_list=True)
        if results:
            return results[0] if return_first_result else results

        return None  # None if not found

    async def add_to_db(self, data: Dict[str, Any]) -> None:
        await self.collection.insert_one(data)
        self._add_to_cache(data)

    async def fetch_and_cache_all(self) -> None:
        results = await self.get_items_in_db({}, to_list=True)
        logging.info(f"[{self.name}]: Found {len(results)} items in database")
        for data in results:
            _id = (
                data.get("guild_id", None)
                or data.get("id", None)
                or data.get("_id", None)
            )
            self.collection_cache[_id] = data

    async def update_db(self, data: Dict[str, Any], new_value: Dict[str, Any]) -> None:
        await self.collection.update_one(data, {"$set": new_value}, upsert=True)
        old_data = await self.find_one_from_db(data)
        self._update_cache(_id=old_data, new_value=new_value)  # type: ignore
        # if result is None:
        #     self._add_to_cache(param_filter=new_value)

    async def remove_from_db(self, data: Dict[str, Any]) -> None:
        await self.collection.delete_one(data)
        self._remove_from_cache(data)
