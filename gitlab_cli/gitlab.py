import shutil
from attrdict import AttrDict
from colorama import Fore
from .config import config
from .constants import *


MAX_WIDTH = shutil.get_terminal_size((80, 20)).columns
OPENER, CLOSER = ((Fore.LIGHTBLACK_EX, Fore.RESET)
                  if config["ui"]["colors_enabled"] else ("", ""))
SPLITTER = MAX_WIDTH * "-"


class ConfigMeta(type):
    def __new__(cls, name, bases, dct):
        obj = type.__new__(cls, name, bases, dct)
        if hasattr(obj, "_name"):
            obj.config = AttrDict(config["gitlab"].get(obj._name, {}))
        return obj


class Base(object, metaclass=ConfigMeta):

    _data = {}
    _splitter = "\n{}{}{}".format(OPENER, SPLITTER, CLOSER)

    def __init__(self, **kwargs):
        self._data = dict.fromkeys(self.config.fields)
        for key, value in kwargs.items():
            if key in self._data:
                self._data[key] = value
        if hasattr(self, "_update") and callable(self._update):
            self._update()

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def fmt(self, inline, **params):
        attr = "list" if inline else "item"

        if config["ui"]["colors_enabled"]:
            color_fields = self.config.get("color_fields")
            if color_fields:
                color_field = color_fields[0]
                params[color_field] = "{}{}{}".format(
                    self.color, self._data[color_field], CLOSER)

        params["splitter"] = self._splitter
        string = self.config['format'].get(attr).format_map(params)
        return string[:MAX_WIDTH] + self._splitter if inline else string

    @property
    def color(self):
        try:
            color_field = self.config.color_fields[0]
            colors = self.config.colors
            color = colors[self[color_field]].upper()
            return getattr(Fore, color)
        except (AttributeError, KeyError):
            pass

    def display(self, inline=False):
        if inline:
            return self.fmt(inline, **self._data)
        return self.fmt(inline, **self._data)

    @classmethod
    def get_path(cls, as_list=False, subitems=False, **kwargs):
        cfg = cls.config.path
        path = cfg.get("list" if as_list else "subitems" if subitems else "item")
        return path.format(**kwargs)


class Registry(object):

    _registry = {}

    @classmethod
    def register(cls, to_register):
        if isinstance(to_register, list):
            for klass in to_register:
                cls._registry[klass._name] = klass
        else:
            klass = to_register
            cls._registry[klass._name] = klass

    @classmethod
    def get_class_for(cls, name):
        return cls._registry.get(name, None)


class Project(Base):

    _name = "project"


class Pipeline(Base):

    _name = "pipeline"

    def _update(self):
        self["username"] = self["user"]["username"] if self["user"] else NOBODY


class Issue(Base):

    _name = "issue"

    def _update(self):
        self["assignee"] = (
            self["assignee"]["username"] if self["assignee"] else NOBODY)


class Note(Base):

    _name = "note"


class User(Base):

    _name = "user"


class Job(Base):

    _name = "job"


class Trace(Base):

    _name = "trace"

    def display(self, inline=False):
        return self["raw_data"]


class Message(Base):

    _name = "message"


class Todo(Message):

    _name = "todo"


Registry.register([
    Project, Pipeline, Issue, Note, User, Job, Trace, Message, Todo
])
