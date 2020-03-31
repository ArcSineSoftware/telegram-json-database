import json
from typing import *
import os
import threading


class TGDatabase:
    def __init__(self, database_path, default_config: Dict, default_user: Dict):
        try:
            os.mkdir(database_path)
        except FileExistsError:
            pass
        self.database_path = os.path.abspath(database_path)
        self.default_config: Dict = default_config
        self.default_user: Dict = default_user

        self._user_lock_obj = threading.Event()
        self._user_lock_obj.set()
        self._config_lock_obj = threading.Event()
        self._config_lock_obj.set()

    def _config_dict_path(self) -> str:
        return f"{self.database_path}/config.json"

    def _user_dict_path(self, tg_id: int) -> str:
        return f"{self.database_path}/user_{tg_id}.json"

    def _lock_config(self):
        """Lock the config database"""
        # Wait until the lock is True
        self._config_lock_obj.wait()
        # Make the lock false
        self._config_lock_obj.clear()

    def _unlock_config(self):
        """Unlock the config database"""
        self._config_lock_obj.set()

    def _lock_user(self):
        """Lock the users' database"""
        # Wait until the lock is True
        self._user_lock_obj.wait()
        # Make the lock false
        self._user_lock_obj.clear()

    def _unlock_user(self):
        """Unlock the users' database"""
        self._user_lock_obj.set()

    def get(self, tg_id: int, key):
        user = self.get_user(tg_id, merge_defaults=False)
        if key in user:
            return user[key]
        elif key in self.default_user:
            return self.default_user[key]
        else:
            return None

    def set(self, tg_id: int, key, value):
        user = self.get_user(tg_id, merge_defaults=False)
        user[key] = value
        self.overwrite_user(tg_id, user)

    def get_user(self, tg_id: int, merge_defaults=True) -> Dict:
        """Get the user's dict, immutable."""
        self._lock_user()
        try:
            with open(self._user_dict_path(tg_id), "r") as fp:
                ret = json.load(fp)
            if merge_defaults:
                for key, value in self.default_user.items():
                    if key not in ret:
                        ret[key] = value
        except FileNotFoundError:
            ret = self.default_user if merge_defaults else {}
        finally:
            self._unlock_user()
        return ret

    def overwrite_user(self, tg_id: int, new_dict: Dict) -> None:
        """Overwrite the user's dict."""
        self._lock_user()
        try:
            with open(self._user_dict_path(tg_id), "w") as fp:
                json.dump(new_dict, fp)
        finally:
            self._unlock_user()

    def config_get(self, key):
        config = self.config_get_dict(merge_defaults=False)
        if key in config:
            return config[key]
        elif key in self.default_config:
            return self.default_config[key]
        else:
            return None

    def config_set(self, key, value):
        config = self.config_get_dict(merge_defaults=False)
        config[key] = value
        self.config_set_dict(config)

    def config_get_dict(self, merge_defaults=True) -> Dict:
        self._lock_config()
        try:
            with open(self._config_dict_path(), "r") as fp:
                ret = json.load(fp)
            if merge_defaults:
                for key, value in self.default_config:
                    if key not in ret:
                        ret[key] = value
        except FileNotFoundError:
            ret = self.default_user if merge_defaults else {}
        finally:
            self._unlock_config()
        return ret

    def config_set_dict(self, new_dict: Dict) -> None:
        self._lock_config()
        try:
            with open(self._config_dict_path(), "w") as fp:
                json.dump(new_dict, fp)
        finally:
            self._unlock_config()
