from dataclasses import dataclass, field
import flyable.data.lang_type as lang_type

@dataclass
class Argument:
    name: str = ""
    type: lang_type.LangType = field(default_factory=lang_type.get_unknown_type)

